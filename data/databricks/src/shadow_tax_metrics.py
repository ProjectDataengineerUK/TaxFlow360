"""Operational Shadow Tax metrics derived only from published Gold versions."""
import dlt
from pyspark.sql import functions as F

@dlt.table(name="gold_shadow_tax_metrics")
def gold_shadow_tax_metrics():
    return (dlt.read("gold_shadow_tax").groupBy("tenant_id","company_tax_id",F.to_date("detected_at").alias("metric_date"))
        .agg(F.count("*").alias("total"),F.sum(F.col("status").startswith("MATCHED").cast("long")).alias("matched"),
             F.sum((F.col("status")=="DIVERGENT").cast("long")).alias("divergent"),F.sum("absolute_difference").alias("materiality"))
        .withColumn("reconciliation_rate",F.when(F.col("total")==0,F.lit(0)).otherwise(F.col("matched")/F.col("total"))))
