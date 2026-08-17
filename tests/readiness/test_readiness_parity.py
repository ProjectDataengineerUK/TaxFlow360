from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from taxflow_query.readiness import DimensionRule, EvidenceFact, Methodology, calculate_assessment


def test_reference_fixture_matches_distributed_contract() -> None:
    names = ("fiscal", "financial", "erp_integrations", "master_data", "payment_methods", "reconciliation", "split_readiness", "working_capital")
    weights = ("0.18", "0.14", "0.13", "0.12", "0.11", "0.13", "0.10", "0.09")
    method = Methodology(version="1.0.0", status="approved",
        dimensions={name: DimensionRule(weight=Decimal(weight)) for name, weight in zip(names, weights, strict=True)})
    facts = [EvidenceFact(evidence_id=f"gold-{i}", dimension=name, score=Decimal(30 + i * 10),
                         source_reference=f"silver-row-{i}") for i, name in enumerate(names)]
    result = calculate_assessment(tenant_id=UUID(int=7), company_tax_id="12345678000199",
        cutoff_at=datetime(2027, 1, 1, tzinfo=timezone.utc), methodology=method, evidence=facts)
    assert result.overall_score == Decimal("60.80")
    assert [item.score for item in result.dimension_scores] == [Decimal(30 + i * 10) for i in range(8)]
    assert result.evidence_count == 8


