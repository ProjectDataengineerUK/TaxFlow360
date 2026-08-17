"""Append-only ingestion of canonical TaxFlow envelopes."""

import dlt
from pyspark.sql import functions as F
from pyspark.sql import types as T

SCHEMA = T.StructType([
    T.StructField("tax_transaction_id", T.StringType()),
    T.StructField("tenant_id", T.StringType()),
    T.StructField("company_tax_id", T.StringType()),
    T.StructField("source_system", T.StringType()),
    T.StructField("source_event_id", T.StringType()),
    T.StructField("occurred_at", T.TimestampType()),
    T.StructField("document_type", T.StringType()),
    T.StructField("document_key", T.StringType()),
    T.StructField("operation_amount", T.DecimalType(20, 6)),
    T.StructField("currency", T.StringType()),
    T.StructField("rule_version", T.StringType()),
    T.StructField("calculation_status", T.StringType()),
    T.StructField("payload_schema_version", T.StringType()),
    T.StructField("ingested_at", T.TimestampType()),
    T.StructField("current_tax_amount", T.DecimalType(20, 6)),
    T.StructField("future_tax_amount", T.DecimalType(20, 6)),
    T.StructField("payment_amount", T.DecimalType(20, 6)),
    T.StructField("due_at", T.TimestampType()),
])


@dlt.table(name="bronze_transactions", comment="Immutable canonical envelopes plus ingestion lineage")
def bronze_transactions():
    source = spark.conf.get("taxflow.source_path")
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .schema(SCHEMA)
        .load(source)
        .withColumn("_source_file", F.input_file_name())
        .withColumn("_bronze_ingested_at", F.current_timestamp())
        .withColumn("_record_hash", F.sha2(F.to_json(F.struct(*SCHEMA.fieldNames())), 256))
    )
