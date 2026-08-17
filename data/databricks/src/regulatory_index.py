"""Provider-neutral Delta Sync index specification for Databricks AI Search."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DeltaSyncIndexSpec:
    source_table:str; primary_key:str="chunk_id"; index_subtype:str="HYBRID"; pipeline_type:str="TRIGGERED"
    columns_to_sync:tuple[str,...]=("chunk_text","document_id","document_version_id","authority_id","document_type","canonical_url","valid_from","valid_to","content_sha256","locator")

def build_index_spec(catalog:str)->DeltaSyncIndexSpec:
    if not catalog.replace("_","").isalnum(): raise ValueError("invalid catalog")
    return DeltaSyncIndexSpec(f"{catalog}.taxflow_regulatory.silver_regulatory_chunk")

if __name__=="__main__": print("index creation requires authenticated hosted Databricks environment")
