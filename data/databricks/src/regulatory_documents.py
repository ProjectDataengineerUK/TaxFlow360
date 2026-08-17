"""Bronze capture ledger and immutable bitemporal Silver document versions."""
import dlt
from pyspark.sql import functions as F

@dlt.table(name="bronze_regulatory_capture")
@dlt.expect_or_drop("manifest_identity","capture_id IS NOT NULL AND authority_id IS NOT NULL AND canonical_url IS NOT NULL AND content_sha256 IS NOT NULL")
def bronze_regulatory_capture(): return spark.readStream.table("regulatory_capture_inbox")

@dlt.table(name="silver_regulatory_document_version")
@dlt.expect_or_fail("official_https","canonical_url LIKE 'https://%' AND length(content_sha256)=64")
def silver_regulatory_document_version():
    return (dlt.read_stream("bronze_regulatory_capture")
        .dropDuplicates(["authority_id","canonical_url","content_sha256"])
        .withColumn("document_id",F.sha2(F.concat_ws("|","authority_id","canonical_url"),256))
        .withColumn("document_version_id",F.sha2(F.concat_ws("|","authority_id","canonical_url","content_sha256"),256))
        .withColumn("temporal_status",F.when(F.col("valid_from").isNull(),"UNKNOWN").otherwise("RESOLVED")))
