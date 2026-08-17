"""Strict, deterministic loader for approved reconciliation policy."""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import json
import re
import yaml

@dataclass(frozen=True)
class ReconciliationPolicy:
    version: str
    checksum: str
    watermark_hours: int
    tolerance: Decimal
    review: Decimal
    high: Decimal
    critical: Decimal

def load_policy(path: str | Path) -> ReconciliationPolicy:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if raw.get("status") != "approved" or not re.fullmatch(r"\d+\.\d+\.\d+", str(raw.get("version"))):
        raise ValueError("policy must be approved and semver-versioned")
    if raw["approval"]["preparedBy"] == raw["approval"]["approvedBy"]:
        raise ValueError("four-eyes approval is required")
    if raw["workflow"] != {"criticalRequiresHumanReview": True, "autoCloseCritical": False}:
        raise ValueError("unsafe workflow policy")
    tolerance = next(item for item in raw["tolerances"] if item["currency"] == "BRL")
    thresholds = raw["materiality"]
    values = [Decimal(thresholds[key]) for key in ("review", "high", "critical")]
    if not Decimal(tolerance["absolute"]) >= 0 or values != sorted(values) or len(set(values)) != 3:
        raise ValueError("invalid tolerance or materiality")
    checksum = sha256(json.dumps(raw, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return ReconciliationPolicy(str(raw["version"]), checksum, int(raw["watermarkHours"]),
        Decimal(tolerance["absolute"]), *values)
