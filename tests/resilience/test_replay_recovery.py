from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'data/databricks/src'))
from reconciliation_policy import load_policy
from shadow_tax_reference import reconcile
def test_replay_order_does_not_change_semantic_fingerprint():
    policy=load_policy(ROOT/'config/reconciliation-policy.yaml'); kwargs=dict(tenant_id='tenant',amounts={x:Decimal('10') for x in ('fiscal','erp','payment','split')},policy=policy,logical_cutoff=datetime(2026,8,17,tzinfo=timezone.utc))
    assert reconcile(source_event_ids=['a','b','c','d'],**kwargs).fingerprint==reconcile(source_event_ids=['d','c','b','a'],**kwargs).fingerprint
