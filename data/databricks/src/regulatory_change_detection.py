"""Deterministic version diff candidates; never publishes tax rules."""
import dlt
from pyspark.sql import Window,functions as F

@dlt.table(name="gold_regulatory_change_candidate")
def gold_regulatory_change_candidate():
    docs=dlt.read("silver_regulatory_document_version")
    window=Window.partitionBy("document_id").orderBy("captured_at")
    return (docs.withColumn("previous_version_id",F.lag("document_version_id").over(window))
        .withColumn("previous_hash",F.lag("content_sha256").over(window))
        .filter(F.col("previous_hash").isNotNull() & (F.col("previous_hash")!=F.col("content_sha256")))
        .withColumn("diff_sha256",F.sha2(F.concat_ws("|","previous_hash","content_sha256"),256))
        .withColumn("status",F.lit("DRAFT")))
