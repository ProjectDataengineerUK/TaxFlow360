from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from taxflow_query import api
from taxflow_query.digital_twin import DailyCashPoint, DigitalTwinProjection, ScenarioProjection, TaxCitation
from taxflow_query.digital_twin_repository import InMemoryDigitalTwinRepository


def projection(tenant: UUID, published: datetime, closing: str) -> DigitalTwinProjection:
    opening = Decimal(closing) - Decimal("10")
    point = DailyCashPoint(projection_date=date(2027, 1, 1), opening_cash=opening,
        inflow=Decimal("20"), outflow=Decimal("5"), tax_split_outflow=Decimal("5"), closing_cash=Decimal(closing))
    scenario = ScenarioProjection(scenario_id="baseline", scenario_kind="baseline", curve=(point,),
        minimum_balance=Decimal(closing), maximum_working_capital_gap=max(Decimal(), Decimal("100") - Decimal(closing)),
        days_below_minimum=int(Decimal(closing) < 100), tax_float_delta=Decimal("5"))
    citation = TaxCitation(simulation_id=uuid4(), rule_id="CBS-1", document_id="LC-214",
        provision="Art. 1", source_url="https://www.gov.br/receitafederal/", content_sha256="a" * 64)
    fingerprint = sha256(f"{tenant}|{published.isoformat()}".encode()).hexdigest()
    return DigitalTwinProjection(projection_id=uuid4(), fingerprint=fingerprint, tenant_id=tenant,
        company_tax_id="12345678000199", assumption_version="1.0.0", assumption_checksum="b" * 64,
        cutoff_at=published, horizon_days=30, model_mode="deterministic_baseline", minimum_cash=Decimal("100"),
        scenarios=(scenario,), tax_citations=(citation,), published_at=published)


def test_latest_history_curve_comparison_citations_and_tenant_isolation(monkeypatch) -> None:
    repository = InMemoryDigitalTwinRepository()
    monkeypatch.setattr(api, "digital_twin_repository", repository)
    tenant = UUID(int=1)
    first = repository.add(projection(tenant, datetime(2027, 1, 1, tzinfo=timezone.utc), "90"))
    second = repository.add(projection(tenant, datetime(2027, 2, 1, tzinfo=timezone.utc), "120"))
    client = TestClient(api.app)
    base = "/v1/companies/12345678000199/digital-twin"
    headers = {"x-tenant-id": str(tenant)}
    latest = client.get(f"{base}/latest", headers=headers)
    assert latest.status_code == 200 and latest.json()["projection_id"] == str(second.projection_id)
    assert latest.json()["tax_citations"][0]["document_id"] == "LC-214"
    assert len(client.get(f"{base}/history", headers=headers).json()) == 2
    assert client.get(f"{base}/{first.projection_id}/curve", headers=headers,
                      params={"scenario_id": "baseline"}).status_code == 200
    comparison = client.get("/v1/companies/12345678000199/digital-twin-comparison", headers=headers,
        params={"from_projection_id": first.projection_id, "to_projection_id": second.projection_id})
    assert comparison.status_code == 200 and comparison.json()["minimum_balance_delta"] == "30"
    denied = client.get(f"{base}/latest", headers={"x-tenant-id": str(UUID(int=2))})
    assert denied.status_code == 404


def test_repository_is_append_only_and_fingerprint_idempotent() -> None:
    repository = InMemoryDigitalTwinRepository()
    item = projection(UUID(int=1), datetime.now(timezone.utc), "100")
    assert repository.add(item) is repository.add(item)
    assert repository.history(item.tenant_id, item.company_tax_id) == (item,)

