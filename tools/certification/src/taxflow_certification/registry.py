from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json,yaml
from .models import GateDefinition

@dataclass(frozen=True)
class Registry:
    version:str; checksum:str; gates:tuple[GateDefinition,...]; human_approvals:tuple[str,...]

def _load(path:str|Path)->dict:return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
def load_registry(path:str|Path)->Registry:
    raw=_load(path)
    if raw.get("status")!="approved" or raw["promotion"]["missingGateStatus"]!="BLOCKED" or not raw["promotion"]["failOnRequiredSkipped"]: raise ValueError("unsafe gate registry")
    if raw["approval"]["preparedBy"]==raw["approval"]["approvedBy"]: raise ValueError("four-eyes registry approval required")
    gates=tuple(GateDefinition(**item) for tier in raw["tiers"] for item in tier["gates"])
    ids=[gate.id for gate in gates]
    if len(ids)!=len(set(ids)) or not gates: raise ValueError("gate IDs must be unique")
    checksum=sha256(json.dumps(raw,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
    return Registry(str(raw["version"]),checksum,gates,tuple(raw["promotion"]["humanApprovals"]))

def validate_environment(path:str|Path)->dict:
    raw=_load(path)
    if raw["status"]!="approved" or not raw["safety"]["syntheticDataOnly"] or not raw["safety"]["teardownRequired"] or raw["safety"]["staticCredentialsAllowed"]: raise ValueError("unsafe certification environment")
    if raw["approval"]["preparedBy"]==raw["approval"]["approvedBy"]: raise ValueError("four-eyes environment approval required")
    return raw
