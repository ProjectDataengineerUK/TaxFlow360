"""Citation-preserving structural chunks; no character-window-only split."""
import dlt
from pyspark.sql import functions as F

@dlt.table(name="silver_regulatory_chunk",table_properties={"delta.enableChangeDataFeed":"true"})
@dlt.expect_or_fail("citeable","chunk_text IS NOT NULL AND locator IS NOT NULL")
def silver_regulatory_chunk():
    docs=dlt.read("silver_regulatory_document_version")
    return (docs.select("*",F.posexplode("provisions").alias("position","provision"))
        .withColumn("locator",F.col("provision.locator"))
        .withColumn("chunk_text",F.trim(F.col("provision.text")))
        .withColumn("chunk_id",F.sha2(F.concat_ws("|","document_version_id",F.col("position"),"locator"),256))
        .filter(F.length("chunk_text")>0)
        .select("chunk_id","document_id","document_version_id","authority_id","document_type","canonical_url","published_at","valid_from","valid_to","content_sha256","locator","chunk_text"))
