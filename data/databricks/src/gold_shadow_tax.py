"""Tenant-qualified Shadow Tax streaming ledger and immutable result versions."""
import dlt
from pyspark.sql import functions as F

WATERMARK = spark.conf.get("taxflow.shadow_tax_watermark", "24 hours")

@dlt.table(name="shadow_event_ledger", comment="Canonical append-only event ledger with disposition")
@dlt.expect_or_drop("identity", "tenant_id IS NOT NULL AND company_tax_id IS NOT NULL AND event_id IS NOT NULL AND event_version IS NOT NULL")
def shadow_event_ledger():
    return (dlt.read_stream("silver_reconciliation_events")
        .withWatermark("event_time", WATERMARK)
        .dropDuplicatesWithinWatermark(["tenant_id","source","event_id","event_version"])
        .withColumn("disposition",F.lit("ACCEPTED")))

@dlt.table(name="gold_shadow_tax", comment="Immutable tenant-scoped four-way reconciliation versions")
@dlt.expect_or_fail("tenant_scope", "tenant_id IS NOT NULL AND company_tax_id IS NOT NULL")
def gold_shadow_tax():
    grouped=(dlt.read_stream("shadow_event_ledger")
        .groupBy(F.window("event_time",WATERMARK),"tenant_id","company_tax_id","tax_transaction_id")
        .agg(F.map_from_entries(F.collect_list(F.struct(F.lower("source"),"amount"))).alias("amounts"),
             F.sort_array(F.collect_set("event_id")).alias("source_event_ids"),F.max("event_time").alias("logical_cutoff_at")))
    values=F.array(*[F.col("amounts").getItem(x) for x in ("fiscal","erp","payment","split")])
    return (grouped.withColumn("source_count",F.size(F.map_keys("amounts")))
        .withColumn("absolute_difference",(F.array_max(values)-F.array_min(values)).cast("decimal(20,2)"))
        .withColumn("status",F.when(F.col("source_count")<4,"DIVERGENT").when(F.col("absolute_difference")==0,"MATCHED").when(F.col("absolute_difference")<=F.lit("0.01").cast("decimal(20,2)"),"MATCHED_WITH_TOLERANCE").otherwise("DIVERGENT"))
        .withColumn("divergence_type",F.when(F.col("source_count")<4,"MISSING_SOURCE").when(F.col("absolute_difference")>F.lit("0.01"),"AMOUNT_MISMATCH"))
        .withColumn("detected_at",F.current_timestamp()))
