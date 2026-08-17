from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import pytest

from taxflow_query.readiness import DimensionRule, EvidenceFact, Methodology, calculate_assessment, weighted_score


DIMENSIONS = ("fiscal", "financial", "erp_integrations", "master_data", "payment_methods", "reconciliation", "split_readiness", "working_capital")
WEIGHTS = ("0.18", "0.14", "0.13", "0.12", "0.11", "0.13", "0.10", "0.09")


def methodology(status: str = "approved") -> Methodology:
    return Methodology(version="1.0.0", status=status,
        dimensions={name: DimensionRule(weight=Decimal(weight)) for name, weight in zip(DIMENSIONS, WEIGHTS, strict=True)})


def evidence(score: str = "80") -> list[EvidenceFact]:
    return [EvidenceFact(evidence_id=f"EV-{name}", dimension=name, score=Decimal(score),
                         source_reference=f"silver/{name}") for name in DIMENSIONS]


def test_methodology_requires_eight_dimensions_and_unit_weight() -> None:
    with pytest.raises(ValueError, match="eight"):
        Methodology(version="1.0.0", status="approved", dimensions={"fiscal": DimensionRule(weight=1)})
    invalid = {name: DimensionRule(weight=Decimal("0.1")) for name in DIMENSIONS}
    with pytest.raises(ValueError, match="sum"):
        Methodology(version="1.0.0", status="approved", dimensions=invalid)


def test_decimal_scoring_is_deterministic_and_explainable() -> None:
    args = dict(tenant_id=UUID(int=1), company_tax_id="12345678000199",
                cutoff_at=datetime(2027, 1, 1, tzinfo=timezone.utc), methodology=methodology(), evidence=evidence("88.125"))
    first = calculate_assessment(**args)
    second = calculate_assessment(**args)
    assert first == second
    assert first.overall_score == Decimal("88.12")
    assert first.status == "published" and len(first.dimension_scores) == 8
    assert all(item.evidence_ids for item in first.dimension_scores)


def test_missing_evidence_produces_draft_with_issue() -> None:
    assessment = calculate_assessment(tenant_id=UUID(int=1), company_tax_id="12345678000199",
        cutoff_at=datetime.now(timezone.utc), methodology=methodology(), evidence=evidence()[:-1])
    assert assessment.status == "draft"
    assert assessment.issues and assessment.published_at is None


def test_weighted_score_rejects_dimension_mismatch() -> None:
    with pytest.raises(ValueError, match="same dimensions"):
        weighted_score({"a": Decimal(1)}, {"b": Decimal(1)})


