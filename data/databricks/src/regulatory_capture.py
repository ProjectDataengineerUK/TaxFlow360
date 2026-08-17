"""Creates capture requests exclusively from the governed source registry."""
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class CaptureTarget:
    source_id:str; authority:str; host:str; path_prefixes:tuple[str,...]

def load_targets(path:str|Path)->tuple[CaptureTarget,...]:
    raw=yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    policy=raw["fetchPolicy"]
    if raw["status"]!="approved" or policy["userSuppliedUrlsAllowed"] or policy["redirectsAllowed"] or policy["privateNetworkTargetsAllowed"]:
        raise ValueError("unsafe regulatory source policy")
    if raw["approval"]["preparedBy"]==raw["approval"]["approvedBy"]: raise ValueError("four-eyes source approval required")
    return tuple(CaptureTarget(s["id"],s["authority"],s["host"],tuple(s["pathPrefixes"])) for s in raw["sources"])

if __name__=="__main__":
    # Production connector orchestration receives only registry targets. This module intentionally
    # exposes no arbitrary-URL CLI argument and performs no live fetch in local/synthetic builds.
    print("regulatory capture requires governed Databricks task configuration")
