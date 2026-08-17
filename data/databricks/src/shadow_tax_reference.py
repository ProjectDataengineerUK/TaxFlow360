"""Runtime-neutral Shadow Tax reference engine used for parity and replay tests."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from hashlib import sha256
import json

SOURCES = ("fiscal", "erp", "payment", "split")

@dataclass(frozen=True)
class ShadowResult:
    status: str
    divergence_type: str | None
    severity: str | None
    difference: Decimal
    fingerprint: str

def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

def reconcile(*, tenant_id: str, amounts: dict[str, Decimal | None], source_event_ids: list[str],
              policy, logical_cutoff: datetime, tax_mismatch: str | None = None) -> ShadowResult:
    missing = [source for source in SOURCES if amounts.get(source) is None]
    present = [_money(value) for value in amounts.values() if value is not None]
    difference = Decimal("0.00") if not present else max(present) - min(present)
    if missing:
        status, dtype = "DIVERGENT", "MISSING_SOURCE"
    elif tax_mismatch in {"RULE", "RATE", "BASE"}:
        status, dtype = "DIVERGENT", f"{tax_mismatch}_MISMATCH"
    elif difference == 0:
        status, dtype = "MATCHED", None
    elif difference <= policy.tolerance:
        status, dtype = "MATCHED_WITH_TOLERANCE", "ROUNDING_MISMATCH"
    else:
        status, dtype = "DIVERGENT", "AMOUNT_MISMATCH"
    severity = None
    if status == "DIVERGENT":
        severity = "CRITICAL" if difference >= policy.critical else "HIGH" if difference >= policy.high else "REVIEW"
    body = {"tenant":tenant_id,"ids":sorted(source_event_ids),"policy":policy.checksum,
            "cutoff":logical_cutoff.isoformat(),"status":status,"type":dtype}
    fingerprint = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return ShadowResult(status, dtype, severity, difference, fingerprint)
