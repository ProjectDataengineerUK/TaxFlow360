from datetime import datetime,timezone
from enum import StrEnum
from typing import Literal
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field,model_validator

class GateStatus(StrEnum): PASS="PASS"; FAIL="FAIL"; BLOCKED="BLOCKED"; SKIPPED_WITH_APPROVAL="SKIPPED_WITH_APPROVAL"
class GateDefinition(BaseModel):
    model_config=ConfigDict(frozen=True)
    id:str; wave:str; required:bool; owner:str; evidenceType:str; timeoutMinutes:int=Field(gt=0); requiredCapabilities:tuple[str,...]=()
class GateResult(BaseModel):
    model_config=ConfigDict(frozen=True)
    run_id:UUID; gate_id:str; attempt:int=Field(ge=1); status:GateStatus; environment:str
    evidence_uri:str|None=None; evidence_sha256:str|None=Field(default=None,pattern=r"^[a-f0-9]{64}$")
    reason:str|None=None; approver_ids:tuple[str,...]=(); started_at:datetime; completed_at:datetime|None=None
    @model_validator(mode="after")
    def evidence_for_terminal_result(self):
        if self.status in {GateStatus.PASS,GateStatus.FAIL} and not (self.evidence_uri and self.evidence_sha256): raise ValueError("PASS/FAIL require content-addressed evidence")
        if self.status==GateStatus.BLOCKED and not self.reason: raise ValueError("BLOCKED requires reason")
        return self
    @classmethod
    def blocked(cls,run_id:UUID,gate_id:str,reason:str):
        now=datetime.now(timezone.utc); return cls(run_id=run_id,gate_id=gate_id,attempt=1,status=GateStatus.BLOCKED,environment="unavailable",reason=reason,started_at=now,completed_at=now)
class Candidate(BaseModel):
    model_config=ConfigDict(frozen=True)
    run_id:UUID=Field(default_factory=uuid4); release_candidate:str; candidate_sha:str=Field(pattern=r"^[a-f0-9]{40,64}$")
    registry_checksum:str=Field(pattern=r"^[a-f0-9]{64}$"); tool_versions:dict[str,str]; logical_cutoff:datetime
class Approval(BaseModel): gate_id:str; actor_id:str; role:str; decision:Literal["approved","rejected"]; justification:str
class Decision(BaseModel): status:Literal["BLOCKED","APPROVED_FOR_RC"]; blockers:tuple[str,...]; candidate_sha:str; matrix_sha256:str
