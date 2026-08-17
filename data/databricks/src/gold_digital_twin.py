"""Tenant-scoped, append-only Digital Twin projections with tax provenance."""

import dlt
from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from digital_twin_config import load_config

CONFIG = load_config(spark.conf.get("taxflow.digital_twin_config_path"))
SOURCE_TABLE = spark.conf.get("taxflow.digital_twin_source_table")
TAX_TABLE = spark.conf.get("taxflow.digital_twin_tax_table")
MODEL_MODE = spark.conf.get("taxflow.digital_twin_model_mode", "deterministic_baseline")
MONEY = T.DecimalType(20, 2)


@dlt.table(
    name="gold_digital_twin_daily",
    comment="Deterministic daily cash ledger; one immutable row per projection/scenario/day",
    partition_cols=["projection_month"],
    table_properties={"quality": "gold", "delta.appendOnly": "true"},
)
@dlt.expect_or_fail("daily_identity", "tenant_id IS NOT NULL AND company_tax_id IS NOT NULL AND projection_date IS NOT NULL")
@dlt.expect_or_fail("cash_reconciles", "closing_cash = opening_cash + inflow - outflow - tax_split_outflow")
@dlt.expect_or_fail("tax_lineage_complete", "tax_split_outflow = 0 OR simulation_ids IS NOT NULL")
def gold_digital_twin_daily():
    finance = (
        spark.read.table(SOURCE_TABLE)
        .select("tenant_id", F.col("company_tax_id_token").alias("company_tax_id"),
                F.to_date("occurred_at").alias("projection_date"), "operation_amount", "payment_amount", "_record_hash")
        .groupBy("tenant_id", "company_tax_id", "projection_date")
        .agg(F.bround(F.sum(F.coalesce("payment_amount", "operation_amount")), 2).cast(MONEY).alias("inflow"),
             F.lit(0).cast(MONEY).alias("outflow"),
             F.sha2(F.concat_ws("|", F.sort_array(F.collect_set("_record_hash"))), 256).alias("finance_fingerprint"))
    )
    tax = (
        spark.read.table(TAX_TABLE).filter("scenario = 'split'")
        .groupBy("tenant_id", "company_tax_id", F.col("effective_date").alias("projection_date"))
        .agg(F.bround(F.sum("split_amount"), 2).cast(MONEY).alias("tax_split_outflow"),
             F.sort_array(F.collect_set("simulation_id")).alias("simulation_ids"),
             F.sort_array(F.flatten(F.collect_set("rule_ids"))).alias("rule_ids"),
             F.array_distinct(F.flatten(F.collect_list("official_sources"))).alias("official_sources"))
    )
    daily = finance.join(tax, ["tenant_id", "company_tax_id", "projection_date"], "left").fillna(0, ["tax_split_outflow"])
    order = Window.partitionBy("tenant_id", "company_tax_id").orderBy("projection_date")
    cumulative = order.rowsBetween(Window.unboundedPreceding, Window.currentRow)
    prior = order.rowsBetween(Window.unboundedPreceding, -1)
    opening_seed = F.lit(str(CONFIG.minimum_cash)).cast(MONEY)
    net = F.col("inflow") - F.col("outflow") - F.col("tax_split_outflow")
    return (
        daily.withColumn("scenario_id", F.lit("baseline"))
        .withColumn("assumption_version", F.lit(CONFIG.version))
        .withColumn("assumption_checksum", F.lit(CONFIG.checksum))
        .withColumn("model_mode", F.lit("deterministic_baseline"))
        .withColumn("model_fallback_reason", F.lit(
            "promoted_model_adapter_unavailable" if MODEL_MODE == "promoted_mlflow" else "model_not_promoted"
        ))
        .withColumn("source_dataset_fingerprint", F.sha2(F.concat_ws("|", F.sort_array(
            F.collect_set("finance_fingerprint").over(Window.partitionBy("tenant_id", "company_tax_id"))
        )), 256))
        .withColumn("projection_id", F.sha2(F.concat_ws("|", "tenant_id", "company_tax_id",
                    F.lit(CONFIG.version), "source_dataset_fingerprint"), 256))
        .withColumn("opening_cash", F.bround(opening_seed + F.coalesce(F.sum(net).over(prior), F.lit(0)), 2).cast(MONEY))
        .withColumn("closing_cash", F.bround(opening_seed + F.sum(net).over(cumulative), 2).cast(MONEY))
        .withColumn("projection_month", F.date_trunc("month", "projection_date").cast("date"))
    )


@dlt.table(name="gold_digital_twin_evidence", comment="Projection drivers and inherited immutable tax lineage",
           table_properties={"quality": "gold", "delta.appendOnly": "true"})
def gold_digital_twin_evidence():
    return (
        dlt.read("gold_digital_twin_daily")
        .select("projection_id", "tenant_id", "company_tax_id", "projection_date", "scenario_id",
                "assumption_version", "assumption_checksum", "finance_fingerprint", "simulation_ids", "rule_ids",
                "official_sources", "model_mode", "model_fallback_reason",
                F.struct("inflow", "outflow", "tax_split_outflow", "opening_cash", "closing_cash").alias("cash_evidence"))
    )


@dlt.table(name="gold_digital_twin_summary", comment="Immutable liquidity and working-capital indicators",
           table_properties={"quality": "gold", "delta.appendOnly": "true"})
@dlt.expect_or_fail("summary_identity", "projection_id IS NOT NULL AND tenant_id IS NOT NULL")
def gold_digital_twin_summary():
    floor = F.lit(str(CONFIG.minimum_cash)).cast(MONEY)
    return (
        dlt.read("gold_digital_twin_daily")
        .groupBy("projection_id", "tenant_id", "company_tax_id", "scenario_id", "assumption_version",
                 "assumption_checksum", "model_mode", "model_fallback_reason")
        .agg(F.min("projection_date").alias("starts_on"), F.max("projection_date").alias("ends_on"),
             F.min("closing_cash").alias("minimum_balance"),
             F.bround(F.max(F.greatest(F.lit(0), floor - F.col("closing_cash"))), 2).cast(MONEY).alias("maximum_working_capital_gap"),
             F.sum((F.col("closing_cash") < floor).cast("int")).alias("days_below_minimum"),
             F.bround(F.sum("tax_split_outflow"), 2).cast(MONEY).alias("tax_float_delta"),
             F.countDistinct("projection_date").alias("projected_days"))
        .withColumn("published_at", F.to_timestamp("ends_on"))
    )
