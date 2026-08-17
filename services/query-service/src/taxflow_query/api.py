from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, HttpUrl

from .readiness import ReadinessAssessment
from .repository import AssessmentNotFound, InMemoryReadinessRepository
from .digital_twin import DigitalTwinComparison, DigitalTwinProjection, ScenarioProjection
from .digital_twin_repository import DigitalTwinNotFound, InMemoryDigitalTwinRepository
from .shadow_tax import ShadowDivergence, ShadowMetrics
from .shadow_tax_repository import InMemoryShadowTaxRepository, ShadowTaxNotFound

app = FastAPI(title="TaxFlow Query API", version="0.1.0")


class Projection(BaseModel):
    scenario: str
    current_tax: Decimal
    projected_tax: Decimal
    working_capital_delta: Decimal


class ReadinessComparison(BaseModel):
    from_assessment_id: UUID
    to_assessment_id: UUID
    overall_delta: Decimal
    dimension_deltas: dict[str, Decimal]


class OfficialSource(BaseModel):
    model_config = ConfigDict(frozen=True)
    source_id: str
    source_url: HttpUrl
    authority: str
    document_id: str
    provision: str
    content_sha256: str


class SimulationScenario(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenario: str
    total_tax: Decimal
    split_amount: Decimal
    components: dict[str, Decimal]
    rule_ids: tuple[str, ...]
    sources: tuple[OfficialSource, ...]


class TaxSimulation(BaseModel):
    model_config = ConfigDict(frozen=True)
    simulation_id: UUID
    tenant_id: UUID
    company_tax_id: str
    operation_id: str
    effective_at: datetime
    rule_set_version: str
    simulation_fingerprint: str
    scenarios: tuple[SimulationScenario, ...]
    created_at: datetime


class SimulationComparison(BaseModel):
    from_simulation_id: UUID
    to_simulation_id: UUID
    scenario_deltas: dict[str, Decimal]


class InMemorySimulationRepository:
    """Append-only local adapter; production adds PostgreSQL FORCE RLS."""

    def __init__(self) -> None:
        self._items: dict[UUID, TaxSimulation] = {}
        self._fingerprints: dict[tuple[UUID, str], UUID] = {}

    def add(self, item: TaxSimulation) -> TaxSimulation:
        key = (item.tenant_id, item.simulation_fingerprint)
        existing = self._fingerprints.get(key)
        if existing is not None:
            return self._items[existing]
        self._items[item.simulation_id] = item
        self._fingerprints[key] = item.simulation_id
        return item

    def get(self, tenant_id: UUID, company_tax_id: str, simulation_id: UUID) -> TaxSimulation:
        item = self._items.get(simulation_id)
        if item is None or item.tenant_id != tenant_id or item.company_tax_id != company_tax_id:
            raise KeyError(simulation_id)
        return item

    def history(self, tenant_id: UUID, company_tax_id: str) -> tuple[TaxSimulation, ...]:
        return tuple(sorted(
            (item for item in self._items.values()
             if item.tenant_id == tenant_id and item.company_tax_id == company_tax_id),
            key=lambda item: (item.created_at, str(item.simulation_id)), reverse=True,
        ))


repository = InMemoryReadinessRepository()
simulation_repository = InMemorySimulationRepository()
digital_twin_repository = InMemoryDigitalTwinRepository()
shadow_tax_repository = InMemoryShadowTaxRepository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/v1/regulatory/authorities")
def regulatory_authorities(x_tenant_id: UUID = Header(...)) -> list[dict[str, str]]:
    del x_tenant_id
    return [
        {"authorityId":"presidencia_republica","name":"Presidência da República","officialUrl":"https://www.planalto.gov.br/"},
        {"authorityId":"receita_federal_brasil","name":"Receita Federal do Brasil","officialUrl":"https://www.gov.br/receitafederal/"},
        {"authorityId":"ministerio_fazenda","name":"Ministério da Fazenda","officialUrl":"https://www.gov.br/fazenda/"},
    ]


@app.get("/v1/companies/{company_tax_id}/readiness/latest", response_model=ReadinessAssessment)
def latest_readiness(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> ReadinessAssessment:
    try:
        return repository.latest(x_tenant_id, company_tax_id)
    except AssessmentNotFound as exc:
        raise HTTPException(status_code=404, detail="assessment not found") from exc


@app.get("/v1/companies/{company_tax_id}/readiness/history", response_model=list[ReadinessAssessment])
def readiness_history(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> tuple[ReadinessAssessment, ...]:
    return repository.history(x_tenant_id, company_tax_id)


@app.get("/v1/companies/{company_tax_id}/readiness/comparison", response_model=ReadinessComparison)
def readiness_comparison(company_tax_id: str, from_assessment_id: UUID, to_assessment_id: UUID,
                         x_tenant_id: UUID = Header(...)) -> ReadinessComparison:
    try:
        before = repository.get(x_tenant_id, company_tax_id, from_assessment_id)
        after = repository.get(x_tenant_id, company_tax_id, to_assessment_id)
    except AssessmentNotFound as exc:
        raise HTTPException(status_code=404, detail="assessment not found") from exc
    before_dimensions = {item.dimension: item.score for item in before.dimension_scores}
    deltas = {item.dimension: item.score - before_dimensions[item.dimension] for item in after.dimension_scores}
    return ReadinessComparison(from_assessment_id=before.assessment_id, to_assessment_id=after.assessment_id,
                               overall_delta=after.overall_score - before.overall_score,
                               dimension_deltas=deltas)


@app.get("/v1/projections", response_model=list[Projection])
def projections(x_tenant_id: UUID = Header(...), horizon_months: int = Query(12, ge=1, le=120)) -> list[Projection]:
    del x_tenant_id
    factor = Decimal(horizon_months) / Decimal(12)
    return [Projection(scenario="CBS/IBS transition", current_tax=Decimal("125000.00") * factor,
                       projected_tax=Decimal("131250.00") * factor,
                       working_capital_delta=Decimal("-6250.00") * factor)]


@app.get("/v1/companies/{company_tax_id}/simulations", response_model=list[TaxSimulation])
def simulation_history(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> tuple[TaxSimulation, ...]:
    return simulation_repository.history(x_tenant_id, company_tax_id)


@app.get("/v1/companies/{company_tax_id}/simulations/{simulation_id}", response_model=TaxSimulation)
def simulation_detail(company_tax_id: str, simulation_id: UUID,
                      x_tenant_id: UUID = Header(...)) -> TaxSimulation:
    try:
        return simulation_repository.get(x_tenant_id, company_tax_id, simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="simulation not found") from exc


@app.get("/v1/companies/{company_tax_id}/simulation-comparison", response_model=SimulationComparison)
def simulation_comparison(company_tax_id: str, from_simulation_id: UUID, to_simulation_id: UUID,
                          x_tenant_id: UUID = Header(...)) -> SimulationComparison:
    try:
        before = simulation_repository.get(x_tenant_id, company_tax_id, from_simulation_id)
        after = simulation_repository.get(x_tenant_id, company_tax_id, to_simulation_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="simulation not found") from exc
    before_totals = {item.scenario: item.total_tax for item in before.scenarios}
    after_totals = {item.scenario: item.total_tax for item in after.scenarios}
    if before_totals.keys() != after_totals.keys():
        raise HTTPException(status_code=409, detail="scenario sets are not comparable")
    return SimulationComparison(from_simulation_id=before.simulation_id, to_simulation_id=after.simulation_id,
                                scenario_deltas={name: after_totals[name] - value for name, value in before_totals.items()})


@app.get("/v1/companies/{company_tax_id}/digital-twin/latest", response_model=DigitalTwinProjection)
def latest_digital_twin(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> DigitalTwinProjection:
    try:
        return digital_twin_repository.latest(x_tenant_id, company_tax_id)
    except DigitalTwinNotFound as exc:
        raise HTTPException(status_code=404, detail="projection not found") from exc


@app.get("/v1/companies/{company_tax_id}/digital-twin/history", response_model=list[DigitalTwinProjection])
def digital_twin_history(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> tuple[DigitalTwinProjection, ...]:
    return digital_twin_repository.history(x_tenant_id, company_tax_id)


@app.get("/v1/companies/{company_tax_id}/digital-twin/{projection_id}/curve", response_model=ScenarioProjection)
def digital_twin_curve(company_tax_id: str, projection_id: UUID, scenario_id: str = Query(..., min_length=1),
                       x_tenant_id: UUID = Header(...)) -> ScenarioProjection:
    try:
        projection = digital_twin_repository.get(x_tenant_id, company_tax_id, projection_id)
    except DigitalTwinNotFound as exc:
        raise HTTPException(status_code=404, detail="projection not found") from exc
    scenario = next((item for item in projection.scenarios if item.scenario_id == scenario_id), None)
    if scenario is None:
        raise HTTPException(status_code=404, detail="scenario not found")
    return scenario


@app.get("/v1/companies/{company_tax_id}/digital-twin-comparison", response_model=DigitalTwinComparison)
def digital_twin_comparison(company_tax_id: str, from_projection_id: UUID, to_projection_id: UUID,
                            scenario_id: str = Query("baseline"),
                            x_tenant_id: UUID = Header(...)) -> DigitalTwinComparison:
    try:
        before = digital_twin_repository.get(x_tenant_id, company_tax_id, from_projection_id)
        after = digital_twin_repository.get(x_tenant_id, company_tax_id, to_projection_id)
    except DigitalTwinNotFound as exc:
        raise HTTPException(status_code=404, detail="projection not found") from exc
    before_scenario = next((item for item in before.scenarios if item.scenario_id == scenario_id), None)
    after_scenario = next((item for item in after.scenarios if item.scenario_id == scenario_id), None)
    if before_scenario is None or after_scenario is None:
        raise HTTPException(status_code=409, detail="scenario is not comparable")
    return DigitalTwinComparison(from_projection_id=before.projection_id, to_projection_id=after.projection_id,
        minimum_balance_delta=after_scenario.minimum_balance - before_scenario.minimum_balance,
        maximum_gap_delta=after_scenario.maximum_working_capital_gap - before_scenario.maximum_working_capital_gap,
        tax_float_delta=after_scenario.tax_float_delta - before_scenario.tax_float_delta)

@app.get("/v1/companies/{company_tax_id}/shadow-tax", response_model=list[ShadowDivergence])
def shadow_tax_history(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> tuple[ShadowDivergence, ...]:
    return shadow_tax_repository.history(x_tenant_id, company_tax_id)

@app.get("/v1/companies/{company_tax_id}/shadow-tax/metrics", response_model=ShadowMetrics)
def shadow_tax_metrics(company_tax_id: str, x_tenant_id: UUID = Header(...)) -> ShadowMetrics:
    return shadow_tax_repository.metrics(x_tenant_id, company_tax_id)

@app.get("/v1/companies/{company_tax_id}/shadow-tax/{divergence_id}", response_model=ShadowDivergence)
def shadow_tax_detail(company_tax_id: str, divergence_id: UUID,
                      x_tenant_id: UUID = Header(...)) -> ShadowDivergence:
    try:
        return shadow_tax_repository.get(x_tenant_id, company_tax_id, divergence_id)
    except ShadowTaxNotFound as exc:
        raise HTTPException(status_code=404, detail="divergence not found") from exc


def run() -> None:
    import uvicorn
    uvicorn.run("taxflow_query.api:app", host="0.0.0.0", port=8081)
