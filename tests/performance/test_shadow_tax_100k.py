from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'data/databricks/src'))
from reconciliation_policy import load_policy
from shadow_tax_reference import reconcile

def test_reference_engine_100k_without_loss():
    policy=load_policy(ROOT/'config/reconciliation-policy.yaml'); cutoff=datetime(2026,8,17,tzinfo=timezone.utc)
    fingerprints=set()
    for i in range(100_000):
        result=reconcile(tenant_id='tenant',amounts={s:Decimal('10') for s in ('fiscal','erp','payment','split')},
            source_event_ids=[f'{i}-{s}' for s in range(4)],policy=policy,logical_cutoff=cutoff)
        fingerprints.add(result.fingerprint)
    assert len(fingerprints)==100_000
