"""Validated, tenant-safe and idempotent Silver representation."""

import dlt
from pyspark.sql import functions as F

REQUIRED = """
  tax_transaction_id IS NOT NULL AND tenant_id IS NOT NULL
  AND source_system IS NOT NULL AND source_event_id IS NOT NULL
  AND occurred_at IS NOT NULL AND ingested_at IS NOT NULL
  AND payload_schema_version IS NOT NULL AND operation_amount IS NOT NULL
"""


@dlt.table(name="silver_transactions_quarantine", comment="Rejected records with non-sensitive diagnostics")
def silver_transactions_quarantine():
    return (
        dlt.read_stream("bronze_transactions")
        .filter(f"NOT ({REQUIRED})")
        .withColumn("quarantine_reason", F.lit("REQUIRED_FIELD_MISSING"))
        .drop("company_tax_id", "document_key")
    )


@dlt.table(name="silver_transactions", comment="Canonical valid transactions; PII tokenized")
@dlt.expect_or_drop("required_contract_fields", REQUIRED)
@dlt.expect_or_drop("supported_currency", "currency IN ('BRL', 'USD', 'EUR')")
@dlt.expect_or_drop("non_negative_amount", "operation_amount >= 0")
def silver_transactions():
    # Supplied by a secret-backed pipeline policy; deliberately has no fallback.
    pii_salt = spark.conf.get("taxflow.pii_salt")
    return (
        dlt.read_stream("bronze_transactions")
        .withWatermark("occurred_at", "7 days")
        .dropDuplicates(["tenant_id", "source_system", "source_event_id"])
        .withColumn("company_tax_id_token", F.sha2(F.concat_ws(":", F.lit(pii_salt), "company_tax_id"), 256))
        .withColumn("document_key_token", F.sha2(F.concat_ws(":", F.lit(pii_salt), "document_key"), 256))
        .drop("company_tax_id", "document_key")
        .withColumn("operation_date", F.to_date("occurred_at"))
    )
