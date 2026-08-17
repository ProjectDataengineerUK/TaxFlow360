"""Offline, deterministic batch simulation from a frozen approved catalog."""

import json

import dlt
from pyspark.sql import functions as F
from pyspark.sql import types as T

from tax_rule_catalog import load_catalog

CATALOG = load_catalog(
    spark.conf.get("taxflow.tax_catalog_path"),
    spark.conf.get("taxflow.source_authorities_path"),
)
SOURCE_TABLE = spark.conf.get("taxflow.simulation_source_table")
MONEY = T.DecimalType(20, 2)


def _rules_frame():
    rows = [(
        rule.rule_id, rule.component, rule.scenario, str(rule.rate), rule.valid_from,
        rule.valid_until, json.dumps([source.__dict__ for source in rule.sources], sort_keys=True),
    ) for rule in CATALOG.rules]
    return spark.createDataFrame(
        rows,
        "rule_id string, component string, scenario string, rate string, valid_from timestamp, valid_until timestamp, sources_json string",
    ).withColumn("rate", F.col("rate").cast(T.DecimalType(12, 8)))


@dlt.table(
    name="gold_tax_simulation_component",
    comment="HALF_EVEN component calculations with frozen rule and official sources",
    partition_cols=["effective_date"],
    table_properties={"quality": "gold", "delta.appendOnly": "true"},
)
@dlt.expect_or_fail("component_identity", "tenant_id IS NOT NULL AND operation_id IS NOT NULL AND rule_id IS NOT NULL")
@dlt.expect_or_fail("official_source_required", "size(official_sources) > 0")
def gold_tax_simulation_component():
    operations = (
        spark.read.table(SOURCE_TABLE)
        .select("tenant_id", F.col("company_tax_id_token").alias("company_tax_id"),
                F.col("tax_transaction_id").alias("operation_id"),
                F.col("occurred_at").alias("effective_at"), "operation_amount", "currency", "_record_hash")
    )
    rules = F.broadcast(_rules_frame())
    matched = operations.join(
        rules,
        (F.col("effective_at") >= F.col("valid_from"))
        & (F.col("valid_until").isNull() | (F.col("effective_at") < F.col("valid_until"))),
        "inner",
    )
    source_schema = "array<struct<source_id:string,source_url:string,authority:string,document_id:string,provision:string,content_sha256:string>>"
    return (
        matched.withColumn("effective_date", F.to_date("effective_at"))
        .withColumn("component_amount", F.bround(F.col("operation_amount") * F.col("rate"), 2).cast(MONEY))
        .withColumn("official_sources", F.from_json("sources_json", source_schema))
        .withColumn("rule_set_version", F.lit(CATALOG.version))
        .withColumn("rule_set_checksum", F.lit(CATALOG.checksum))
        .withColumn("simulation_fingerprint", F.sha2(F.concat_ws("|", "tenant_id", "company_tax_id", "operation_id",
                    "scenario", F.col("effective_at").cast("string"), F.lit(CATALOG.version), "_record_hash"), 256))
        .withColumn("simulation_id", F.col("simulation_fingerprint"))
        .select("simulation_id", "simulation_fingerprint", "tenant_id", "company_tax_id", "operation_id",
                "effective_at", "effective_date", "currency", "scenario", "component", "component_amount",
                "rule_id", "rule_set_version", "rule_set_checksum", "official_sources", "_record_hash")
    )


@dlt.table(
    name="gold_tax_simulation",
    comment="Immutable scenario totals and complete calculation memory",
    partition_cols=["effective_date"],
    table_properties={"quality": "gold", "delta.appendOnly": "true"},
)
@dlt.expect_or_fail("simulation_identity", "tenant_id IS NOT NULL AND company_tax_id IS NOT NULL AND operation_id IS NOT NULL")
@dlt.expect_or_fail("simulation_has_sources", "size(official_sources) > 0")
def gold_tax_simulation():
    return (
        dlt.read("gold_tax_simulation_component")
        .groupBy("simulation_id", "simulation_fingerprint", "tenant_id", "company_tax_id", "operation_id",
                 "effective_at", "effective_date", "currency", "scenario", "rule_set_version", "rule_set_checksum")
        .agg(
            F.bround(F.sum("component_amount"), 2).cast(MONEY).alias("total_tax"),
            F.sort_array(F.collect_list(F.struct("component", "component_amount", "rule_id"))).alias("calculation_memory"),
            F.array_distinct(F.flatten(F.collect_list("official_sources"))).alias("official_sources"),
            F.sort_array(F.collect_set("rule_id")).alias("rule_ids"),
        )
        .withColumn("split_amount", F.when(F.col("scenario") == "split", F.col("total_tax")).otherwise(F.lit(0).cast(MONEY)))
        .withColumn("published_at", F.col("effective_at"))
    )
