from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient

from taxflow_query import api
from taxflow_query.readiness import DimensionRule, EvidenceFact, Methodology, calculate_assessment
from taxflow_query.repository import InMemoryReadinessRepository

DIMS = ("fiscal", "financial", "erp_integrations", "master_data", "payment_methods", "reconciliation", "split_readiness", "working_capital")
WEIGHTS = ("0.18", "0.14", "0.13", "0.12", "0.11", "0.13", "0.10", "0.09")


def assessment(tenant: UUID, cutoff: datetime, score: str):
    method = Methodology(version="1.0.0", status="approved",
        dimensions={name: DimensionRule(weight=Decimal(weight)) for name, weight in zip(DIMS, WEIGHTS, strict=True)})
    facts = [EvidenceFact(evidence_id=name, dimension=name, score=Decimal(score), source_reference=name) for name in DIMS]
    return calculate_assessment(tenant_id=tenant, company_tax_id="12345678000199", cutoff_at=cutoff,
                                methodology=method, evidence=facts)


def test_latest_history_comparison_and_tenant_isolation(monkeypatch) -> None:
    repo = InMemoryReadinessRepository()
    monkeypatch.setattr(api, "repository", repo)
    tenant = UUID(int=1)
    first = repo.add(assessment(tenant, datetime(2027, 1, 1, tzinfo=timezone.utc), "70"))
    second = repo.add(assessment(tenant, datetime(2027, 2, 1, tzinfo=timezone.utc), "90"))
    client = TestClient(api.app)
    path = "/v1/companies/12345678000199/readiness"
    headers = {"x-tenant-id": str(tenant)}
    assert client.get(f"{path}/latest", headers=headers).json()["assessment_id"] == str(second.assessment_id)
    assert len(client.get(f"{path}/history", headers=headers).json()) == 2
    comparison = client.get(f"{path}/comparison", headers=headers,
        params={"from_assessment_id": first.assessment_id, "to_assessment_id": second.assessment_id})
    assert comparison.status_code == 200 and comparison.json()["overall_delta"] == "20.00"
    assert client.get(f"{path}/latest", headers={"x-tenant-id": str(UUID(int=2))}).status_code == 404


def test_repository_is_append_only_and_idempotent() -> None:
    repo = InMemoryReadinessRepository()
    item = assessment(UUID(int=1), datetime.now(timezone.utc), "80")
    assert repo.add(item) is repo.add(item)
    assert repo.history(item.tenant_id, item.company_tax_id) == (item,)


