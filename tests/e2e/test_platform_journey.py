from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys,yaml
ROOT=Path(__file__).resolve().parents[2]; sys.path[:0]=[str(ROOT/'data/databricks/src'),str(ROOT/'services/regulatory-service/src')]
from reconciliation_policy import load_policy
from shadow_tax_reference import reconcile
from taxflow_regulatory.source_validator import ApprovedSource,validate_url

def test_synthetic_journey_preserves_identity_amounts_and_official_source():
    journey=yaml.safe_load((ROOT/'tests/e2e/fixtures/platform-journey.yaml').read_text()); assert len(journey['expectedProducts'])==6
    policy=load_policy(ROOT/'config/reconciliation-policy.yaml'); fingerprints=set()
    for tenant in journey['tenants']:
        amounts={k:Decimal(v) for k,v in tenant['sources'].items()}; result=reconcile(tenant_id=tenant['tenantId'],amounts=amounts,source_event_ids=[tenant['transactionId']+'-'+k for k in amounts],policy=policy,logical_cutoff=datetime.fromisoformat(journey['logicalCutoff'].replace('Z','+00:00')))
        fingerprints.add(result.fingerprint)
    assert len(fingerprints)==2
    source=ApprovedSource('planalto','www.planalto.gov.br',('/ccivil_03/',)); assert validate_url(journey['officialSource']['url'],(source,)).source_id=='planalto'
