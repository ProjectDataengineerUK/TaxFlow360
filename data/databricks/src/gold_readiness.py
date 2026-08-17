"""Deterministic evidence, eight dimensions and immutable Readiness Gold."""

import dlt
from pyspark.sql import functions as F
from pyspark.sql import types as T

from readiness_methodology import DIMENSIONS, load_methodology

METHODOLOGY = load_methodology(spark.conf.get("taxflow.readiness_methodology_path"))
CUTOFF_AT = spark.conf.get("taxflow.readiness_cutoff_at")
SOURCE_TABLE = spark.conf.get("taxflow.readiness_source_table")
DECIMAL = T.DecimalType(7, 2)
EMPTY_RECOMMENDATIONS = F.from_json(
    F.lit("[]"),
    "array<struct<recommendation_id:string,dimension:string,severity:string,action:string,evidence_ids:array<string>>>",
)
EMPTY_DRAFT_ISSUES = F.from_json(F.lit("[]"), "array<struct<code:string,dimension:string,message:string>>")


def _evidence_row(evidence_id: str, value, source_metric: str):
    return F.struct(
        F.lit(evidence_id).alias("evidence_id"),
        value.cast(T.DecimalType(12, 6)).alias("evidence_value"),
        F.lit(source_metric).alias("source_metric"),
    )


def _source():
    return spark.read.table(SOURCE_TABLE).filter(F.col("occurred_at") <= F.to_timestamp(F.lit(CUTOFF_AT)))


@dlt.table(
    name="readiness_evidence",
    comment="Stable, non-sensitive facts explaining every readiness contribution",
    partition_cols=["assessment_date"],
    table_properties={"quality": "gold", "delta.appendOnly": "true"},
)
@dlt.expect_or_fail("evidence_has_tenant", "tenant_id IS NOT NULL")
@dlt.expect_or_fail("evidence_value_present", "evidence_value IS NOT NULL")
def readiness_evidence():
    base = _source().groupBy("tenant_id", "company_tax_id_token").agg(
        F.count("*").alias("transaction_count"),
        F.countDistinct("source_system").alias("source_count"),
        F.avg(F.col("rule_version").isNotNull().cast("double")).alias("rule_coverage"),
        F.avg((F.col("calculation_status") == "CALCULATED").cast("double")).alias("calculation_coverage"),
        F.avg(F.col("payment_amount").isNotNull().cast("double")).alias("payment_coverage"),
        F.avg(F.col("future_tax_amount").isNotNull().cast("double")).alias("future_tax_coverage"),
        F.avg(F.col("due_at").isNotNull().cast("double")).alias("due_date_coverage"),
        F.avg(F.col("payload_schema_version").isNotNull().cast("double")).alias("contract_coverage"),
        F.avg((F.col("ingested_at") <= F.to_timestamp(F.lit(CUTOFF_AT))).cast("double")).alias("freshness_coverage"),
        F.avg(F.col("company_tax_id_token").isNotNull().cast("double")).alias("registration_coverage"),
        F.sum("operation_amount").alias("gross_amount"),
        F.sha2(F.concat_ws("|", F.sort_array(F.collect_set("_record_hash"))), 256).alias("source_dataset_fingerprint"),
        F.max("ingested_at").alias("latest_source_at"),
    )
    evidence = F.array(
        _evidence_row("fiscal.document_completeness_rate", F.col("rule_coverage"), "rule_coverage"),
        _evidence_row("fiscal.classification_consistency_rate", F.col("calculation_coverage"), "calculation_coverage"),
        _evidence_row("financial.settlement_coverage_rate", F.col("payment_coverage"), "payment_coverage"),
        _evidence_row("financial.valid_due_date_rate", F.col("due_date_coverage"), "due_date_coverage"),
        _evidence_row("integration.contract_compliance_rate", F.col("contract_coverage"), "contract_coverage"),
        _evidence_row("integration.records_within_sla_rate", F.col("freshness_coverage"), "freshness_coverage"),
        _evidence_row("master_data.required_fields_complete_rate", F.col("registration_coverage"), "registration_coverage"),
        _evidence_row("master_data.valid_registration_rate", F.col("registration_coverage"), "registration_coverage"),
        _evidence_row("payments.identified_method_rate", F.col("payment_coverage"), "payment_coverage"),
        _evidence_row("payments.traceable_transaction_rate", F.col("payment_coverage"), "payment_coverage"),
        _evidence_row("reconciliation.matched_transaction_rate", F.col("calculation_coverage"), "calculation_coverage"),
        _evidence_row("reconciliation.within_sla_rate", F.col("freshness_coverage"), "freshness_coverage"),
        _evidence_row("split.required_data_coverage_rate", F.least(F.col("payment_coverage"), F.col("future_tax_coverage")), "split_input_coverage"),
        _evidence_row("split.successful_simulation_rate", F.col("future_tax_coverage"), "future_tax_coverage"),
        _evidence_row("working_capital.cash_flow_input_coverage_rate", F.least(F.col("payment_coverage"), F.col("due_date_coverage")), "cash_flow_input_coverage"),
        _evidence_row("working_capital.projected_liquidity_buffer_rate", F.when(F.col("gross_amount") >= 0, F.lit(1)).otherwise(F.lit(0)), "liquidity_buffer"),
    )
    return (
        base.withColumn("cutoff_at", F.to_timestamp(F.lit(CUTOFF_AT)))
        .withColumn("methodology_version", F.lit(METHODOLOGY.version))
        .withColumn("methodology_checksum", F.lit(METHODOLOGY.checksum))
        .withColumn("assessment_fingerprint", F.sha2(F.concat_ws("|", "tenant_id", "company_tax_id_token", F.lit(CUTOFF_AT), F.lit(METHODOLOGY.version)), 256))
        .withColumn("assessment_id", F.col("assessment_fingerprint"))
        .withColumn("assessment_date", F.to_date("cutoff_at"))
        .withColumn("evidence", F.explode(evidence))
        .select("assessment_id", "assessment_fingerprint", "assessment_date", "tenant_id",
                "company_tax_id_token", "cutoff_at", "methodology_version", "methodology_checksum",
                "latest_source_at", "source_dataset_fingerprint", "transaction_count", "evidence.*")
    )


@dlt.table(
    name="readiness_dimension_score",
    comment="Exactly eight deterministic dimension scores per assessment",
    partition_cols=["assessment_date"],
    table_properties={"quality": "gold", "delta.appendOnly": "true"},
)
@dlt.expect_or_fail("dimension_score_range", "dimension_score BETWEEN 0 AND 100")
def readiness_dimension_score():
    criteria = spark.createDataFrame(
        [(item.name, str(item.weight), item.minimum_evidence, criterion.id, criterion.evidence,
          criterion.operator, str(criterion.target), str(criterion.points))
         for item in METHODOLOGY.dimensions for criterion in item.criteria],
        "dimension string, weight string, minimum_evidence int, criterion_id string, evidence_id string, operator string, target string, points string",
    ).select("dimension", F.col("weight").cast(T.DecimalType(8, 6)).alias("weight"), "minimum_evidence",
             "criterion_id", "evidence_id", "operator", F.col("target").cast(T.DecimalType(12, 6)).alias("target"),
             F.col("points").cast(DECIMAL).alias("points"))
    evaluated = (
        dlt.read("readiness_evidence").join(F.broadcast(criteria), "evidence_id", "inner")
        .withColumn("passed",
            F.when(F.col("operator") == "greater_than_or_equal", F.col("evidence_value") >= F.col("target"))
            .when(F.col("operator") == "less_than_or_equal", F.col("evidence_value") <= F.col("target"))
            .when(F.col("operator") == "equal", F.col("evidence_value") == F.col("target"))
            .otherwise(F.lit(False)))
        .withColumn("contribution", F.when(F.col("passed"), F.col("points")).otherwise(F.lit(0).cast(DECIMAL)))
        .withColumn("outcome", F.when(F.col("passed"), "passed").otherwise("failed"))
    )
    return (
        evaluated
        .groupBy("assessment_id", "assessment_fingerprint", "assessment_date", "tenant_id",
                 "company_tax_id_token", "cutoff_at", "methodology_version", "methodology_checksum",
                 "source_dataset_fingerprint", "latest_source_at", "dimension")
        .agg(F.round(F.sum("contribution"), 2).cast(DECIMAL).alias("dimension_score"),
             F.count("evidence_id").alias("evidence_count"),
             F.sort_array(F.collect_set("evidence_id")).alias("evidence_ids"),
             F.sort_array(F.collect_list(F.struct(
                 "evidence_id", "dimension", "criterion_id", "outcome",
                 F.col("source_metric").alias("source_reference"),
                 F.col("evidence_value").cast("string").alias("observed_value"), "contribution"
             ))).alias("evidence"))
        .join(F.broadcast(weights), "dimension")
        .withColumn("eligible", F.col("evidence_count") >= F.col("minimum_evidence"))
    )


@dlt.table(
    name="readiness_assessment",
    comment="Immutable assessment identity, overall score, dimensions and publication state",
    partition_cols=["assessment_date"],
    table_properties={"quality": "gold", "delta.appendOnly": "true"},
)
@dlt.expect_or_fail("exactly_eight_dimensions", "dimension_count = 8")
@dlt.expect_or_fail("overall_score_range", "overall_score BETWEEN 0 AND 100")
def readiness_assessment():
    dimensions = dlt.read("readiness_dimension_score")
    result = dimensions.groupBy(
        "assessment_id", "assessment_fingerprint", "assessment_date", "tenant_id",
        "company_tax_id_token", "cutoff_at", "methodology_version", "methodology_checksum",
        "source_dataset_fingerprint", "latest_source_at",
    ).agg(
        F.round(F.sum(F.col("dimension_score") * F.col("weight")), 2).cast(DECIMAL).alias("overall_score"),
        F.countDistinct("dimension").alias("dimension_count"),
        F.min(F.col("eligible").cast("int")).cast("boolean").alias("all_dimensions_eligible"),
        F.sum("evidence_count").alias("evidence_count"),
        F.sort_array(F.collect_list(F.struct("dimension", F.col("dimension_score").alias("score")))).alias("dimension_scores"),
        F.flatten(F.collect_list("evidence")).alias("evidence"),
    )
    return (
        result.withColumn("classification",
            F.when(F.col("overall_score") < F.lit(str(METHODOLOGY.critical)).cast(DECIMAL), "critical")
            .when(F.col("overall_score") < F.lit(str(METHODOLOGY.attention)).cast(DECIMAL), "attention")
            .when(F.col("overall_score") < F.lit(str(METHODOLOGY.ready)).cast(DECIMAL), "progressing")
            .otherwise("ready"))
        .withColumn("status", F.when(
            F.col("all_dimensions_eligible") & F.lit(METHODOLOGY.status == "published"), "published"
        ).otherwise("draft"))
        .withColumn("overall_score", F.when(F.col("status") == "published", F.col("overall_score")))
        .withColumn("classification", F.when(F.col("status") == "published", F.col("classification")))
        .withColumn("methodology_status", F.lit(METHODOLOGY.status))
        .withColumn("company_tax_id", F.col("company_tax_id_token"))
        .withColumn("input_closed_at", F.col("latest_source_at"))
        .withColumn("assessed_at", F.col("cutoff_at"))
        .withColumn("published_at", F.when(F.col("status") == "published", F.col("cutoff_at")))
        .withColumn("recommendations", EMPTY_RECOMMENDATIONS)
        .withColumn("draft_issues", F.when(F.col("status") == "draft", F.array(F.struct(
            F.lit("NOT_ELIGIBLE_OR_UNPUBLISHED").alias("code"), F.lit(None).cast("string").alias("dimension"),
            F.lit("Evidence eligibility and approved methodology are required for publication.").alias("message")
        ))).otherwise(EMPTY_DRAFT_ISSUES))
        .withColumn("contract_version", F.lit("1.0.0"))
    )
