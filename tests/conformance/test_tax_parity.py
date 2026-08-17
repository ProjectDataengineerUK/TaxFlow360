from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'data/databricks/src'))
from reconciliation_policy import load_policy
from shadow_tax_reference import reconcile
def test_half_even_reconciliation_is_stable_across_replay():
    policy=load_policy(ROOT/'config/reconciliation-policy.yaml'); kwargs=dict(tenant_id='t',amounts={x:Decimal('10.005') for x in ('fiscal','erp','payment','split')},source_event_ids=['f','e','p','s'],policy=policy,logical_cutoff=datetime(2026,8,17,tzinfo=timezone.utc))
    assert reconcile(**kwargs)==reconcile(**kwargs)
