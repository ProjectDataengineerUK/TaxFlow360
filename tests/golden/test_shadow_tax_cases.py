from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "databricks" / "src"))
from reconciliation_policy import load_policy
from shadow_tax_reference import reconcile

POLICY = load_policy(ROOT / "config" / "reconciliation-policy.yaml")

def test_golden_cases():
    cases = yaml.safe_load((ROOT / "tests/golden/shadow-tax-cases.yaml").read_text())["cases"]
    for case in cases:
        amounts = {key: Decimal(value) if value is not None else None for key, value in case["amounts"].items()}
        result = reconcile(tenant_id="tenant-a", amounts=amounts, source_event_ids=list(amounts),
            policy=POLICY, logical_cutoff=datetime(2026, 8, 17, tzinfo=timezone.utc))
        assert result.status == case["expected"], case["id"]

def test_replay_and_duplicate_order_are_deterministic():
    kwargs = dict(tenant_id="tenant-a", amounts={x:Decimal("10") for x in ("fiscal","erp","payment","split")},
        policy=POLICY, logical_cutoff=datetime(2026, 8, 17, tzinfo=timezone.utc))
    assert reconcile(source_event_ids=["b","a","a"], **kwargs).fingerprint == reconcile(source_event_ids=["a","b","a"], **kwargs).fingerprint
