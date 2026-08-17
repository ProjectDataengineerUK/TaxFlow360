from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from hashlib import sha256
from json import dumps
from typing import Literal
from uuid import UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

ASSESSMENT_NAMESPACE = UUID("0bf84b8e-af15-4e80-8c1f-dfb69ac94a2b")


class DimensionRule(BaseModel):
    model_config = ConfigDict(frozen=True)
    weight: Decimal = Field(gt=0, le=1)
    minimum_evidence: int = Field(default=1, ge=1)


class Methodology(BaseModel):
    model_config = ConfigDict(frozen=True)
    version: str = Field(pattern=r"^[1-9]\d*\.\d+\.\d+$")
    status: Literal["draft", "approved"]
    dimensions: dict[str, DimensionRule]
    critical_threshold: Decimal = Decimal("50")
    attention_threshold: Decimal = Decimal("75")
    ready_threshold: Decimal = Decimal("90")

    @model_validator(mode="after")
    def validate_invariants(self) -> "Methodology":
        if len(self.dimensions) != 8:
            raise ValueError("methodology must define exactly eight dimensions")
        if sum((rule.weight for rule in self.dimensions.values()), Decimal()) != Decimal("1"):
            raise ValueError("dimension weights must sum exactly to 1")
        if not self.critical_threshold < self.attention_threshold < self.ready_threshold:
            raise ValueError("thresholds must be strictly increasing")
        return self


class EvidenceFact(BaseModel):
    model_config = ConfigDict(frozen=True)
    evidence_id: str = Field(min_length=1)
    dimension: str = Field(min_length=1)
    score: Decimal = Field(ge=0, le=100)
    source_reference: str = Field(min_length=1)


class DimensionScore(BaseModel):
    model_config = ConfigDict(frozen=True)
    dimension: str
    score: Decimal = Field(ge=0, le=100)
    weight: Decimal
    evidence_ids: tuple[str, ...]
    recommendation: str | None = None


class ReadinessAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)
    assessment_id: UUID
    fingerprint: str
    tenant_id: UUID
    company_tax_id: str = Field(pattern=r"^\d{11}(\d{3})?$")
    methodology_version: str
    cutoff_at: datetime
    overall_score: Decimal = Field(ge=0, le=100)
    classification: Literal["critical", "attention", "progressing", "ready"]
    dimension_scores: tuple[DimensionScore, ...]
    evidence_count: int = Field(ge=0)
    status: Literal["draft", "published", "invalidated"]
    issues: tuple[str, ...] = ()
    published_at: datetime | None = None

    @field_validator("dimension_scores")
    @classmethod
    def exactly_eight_dimensions(cls, value: tuple[DimensionScore, ...]) -> tuple[DimensionScore, ...]:
        if len(value) != 8:
            raise ValueError("assessment must contain exactly eight dimensions")
        return value


def weighted_score(scores: dict[str, Decimal], weights: dict[str, Decimal]) -> Decimal:
    if scores.keys() != weights.keys():
        raise ValueError("scores and weights must contain the same dimensions")
    if sum(weights.values(), Decimal()) != Decimal("1"):
        raise ValueError("weights must sum to 1")
    total = sum((scores[name] * weights[name] for name in sorted(scores)), Decimal())
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


def assessment_fingerprint(tenant_id: UUID, company_tax_id: str, cutoff_at: datetime,
                           methodology_version: str) -> str:
    payload = {"tenant_id": str(tenant_id), "company_tax_id": company_tax_id,
               "cutoff_at": cutoff_at.astimezone(timezone.utc).isoformat(),
               "methodology_version": methodology_version}
    return sha256(dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def calculate_assessment(*, tenant_id: UUID, company_tax_id: str, cutoff_at: datetime,
                         methodology: Methodology, evidence: list[EvidenceFact]) -> ReadinessAssessment:
    if cutoff_at.tzinfo is None:
        raise ValueError("cutoff_at must include a timezone")
    grouped: dict[str, list[EvidenceFact]] = defaultdict(list)
    for fact in evidence:
        if fact.dimension not in methodology.dimensions:
            raise ValueError(f"unknown evidence dimension: {fact.dimension}")
        grouped[fact.dimension].append(fact)
    dimensions: list[DimensionScore] = []
    issues: list[str] = []
    for name, rule in methodology.dimensions.items():
        facts = sorted(grouped[name], key=lambda item: item.evidence_id)
        if len(facts) < rule.minimum_evidence:
            issues.append(f"{name}: requires {rule.minimum_evidence} evidence fact(s)")
        score = (sum((fact.score for fact in facts), Decimal()) / len(facts) if facts else Decimal())
        score = score.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        dimensions.append(DimensionScore(dimension=name, score=score, weight=rule.weight,
            evidence_ids=tuple(fact.evidence_id for fact in facts),
            recommendation=f"Improve {name}" if score < methodology.attention_threshold else None))
    scores = {item.dimension: item.score for item in dimensions}
    weights = {name: rule.weight for name, rule in methodology.dimensions.items()}
    overall = weighted_score(scores, weights)
    classification = ("ready" if overall >= methodology.ready_threshold else
                      "progressing" if overall >= methodology.attention_threshold else
                      "attention" if overall >= methodology.critical_threshold else "critical")
    fingerprint = assessment_fingerprint(tenant_id, company_tax_id, cutoff_at, methodology.version)
    published = methodology.status == "approved" and not issues
    return ReadinessAssessment(assessment_id=uuid5(ASSESSMENT_NAMESPACE, fingerprint), fingerprint=fingerprint,
        tenant_id=tenant_id, company_tax_id=company_tax_id, methodology_version=methodology.version,
        cutoff_at=cutoff_at.astimezone(timezone.utc), overall_score=overall, classification=classification,
        dimension_scores=tuple(dimensions), evidence_count=len(evidence),
        status="published" if published else "draft", issues=tuple(issues),
        published_at=cutoff_at.astimezone(timezone.utc) if published else None)
