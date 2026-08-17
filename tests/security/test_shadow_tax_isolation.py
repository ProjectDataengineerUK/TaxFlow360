from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'services/query-service/src'))
from taxflow_query.shadow_tax import ShadowDivergence, ShadowEvidence
from taxflow_query.shadow_tax_repository import InMemoryShadowTaxRepository, ShadowTaxNotFound

def test_cross_tenant_lookup_does_not_disclose():
    repo=InMemoryShadowTaxRepository(); tenant=uuid4(); now=datetime.now(timezone.utc)
    item=ShadowDivergence(divergence_id=uuid4(),reconciliation_id=uuid4(),version=1,tenant_id=tenant,
        company_tax_id='12345678000199',tax_transaction_id='tx',status='PENDING_HUMAN_REVIEW',
        divergence_type='AMOUNT_MISMATCH',severity='CRITICAL',absolute_difference=Decimal('10000'),
        policy_version='1.0.0',fingerprint='a'*64,logical_cutoff_at=now,detected_at=now,
        source_event_ids=('a',),evidence=ShadowEvidence())
    repo.add(item)
    try: repo.get(uuid4(),item.company_tax_id,item.divergence_id)
    except ShadowTaxNotFound: pass
    else: raise AssertionError('cross-tenant disclosure')
