from datetime import datetime, timezone
from decimal import Decimal
from time import perf_counter
from uuid import UUID

from taxflow_query.readiness import DimensionRule, EvidenceFact, Methodology, calculate_assessment


def test_reference_engine_handles_100k_evidence_under_local_gate() -> None:
    names = ("fiscal", "financial", "erp_integrations", "master_data", "payment_methods", "reconciliation", "split_readiness", "working_capital")
    weights = ("0.18", "0.14", "0.13", "0.12", "0.11", "0.13", "0.10", "0.09")
    method = Methodology(version="1.0.0", status="approved",
        dimensions={name: DimensionRule(weight=Decimal(weight)) for name, weight in zip(names, weights, strict=True)})
    facts = [EvidenceFact(evidence_id=f"EV-{i:06d}", dimension=names[i % 8], score=Decimal(i % 101),
                          source_reference=f"silver/{i}") for i in range(100_000)]
    started = perf_counter()
    result = calculate_assessment(tenant_id=UUID(int=1), company_tax_id="12345678000199",
        cutoff_at=datetime(2027, 1, 1, tzinfo=timezone.utc), methodology=method, evidence=facts)
    assert perf_counter() - started < 60
    assert result.evidence_count == 100_000 and result.status == "published"


