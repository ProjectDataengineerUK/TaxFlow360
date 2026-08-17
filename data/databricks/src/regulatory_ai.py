"""Governance dataset for human-approved regulatory proposals.

This pipeline never changes production rules. It only identifies candidate records
that must be reviewed through the transactional approval workflow.
"""

import dlt
from pyspark.sql import functions as F


@dlt.table(name="regulatory_review_queue", comment="Candidates requiring four-eyes approval")
def regulatory_review_queue():
    return (
        dlt.read("gold_shadow_tax")
        .filter("severity IN ('CRITICAL', 'HIGH')")
        .select("tenant_id", "tax_transaction_id", "rule_version", "severity",
                "absolute_divergence", "_record_hash")
        .withColumn("proposal_status", F.lit("PENDING_HUMAN_REVIEW"))
        .withColumn("automation_allowed", F.lit(False))
        .withColumn("required_approvals", F.lit(2))
        .withColumn("queued_at", F.current_timestamp())
    )
