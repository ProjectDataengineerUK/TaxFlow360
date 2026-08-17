from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

class Chunk(BaseModel):
    model_config=ConfigDict(frozen=True)
    chunk_id:str; document_version_id:str; authority_id:str; document_type:str; jurisdiction:str
    canonical_url:HttpUrl; document_id:str; locator:str; text:str; content_sha256:str=Field(pattern=r"^[a-f0-9]{64}$")
    published_at:datetime|None=None; valid_from:datetime|None=None; valid_to:datetime|None=None
    score:float=0.0; tenant_id:UUID|None=None

class Claim(BaseModel):
    model_config=ConfigDict(frozen=True)
    text:str=Field(min_length=1); citation_chunk_ids:tuple[str,...]=Field(min_length=1)

class Citation(BaseModel):
    chunk_id:str; document_id:str; document_version_id:str; authority_id:str; locator:str
    canonical_url:HttpUrl; content_sha256:str

class CopilotAnswer(BaseModel):
    disposition:Literal["answered","refused","conflicted","failed"]
    claims:tuple[Claim,...]=(); citations:tuple[Citation,...]=(); reason:str|None=None
    cutoff_at:datetime; policy_version:str; model_version:str

class ChangeRequest(BaseModel):
    model_config=ConfigDict(frozen=True)
    change_request_id:UUID; tenant_id:UUID; version:int=Field(ge=1)
    status:Literal["DRAFT","SUBMITTED","APPROVED","REJECTED"]
    source_document_version_ids:tuple[str,...]=Field(min_length=1); affected_rule_ids:tuple[str,...]
    diff_sha256:str=Field(pattern=r"^[a-f0-9]{64}$"); created_by:str
    submitted_by:str|None=None; approved_by:str|None=None; justification:str|None=None
    golden_tests_passed:bool=False
