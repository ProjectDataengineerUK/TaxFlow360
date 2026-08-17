from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

class ShadowEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)
    simulation_ids: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()
    memory_ids: tuple[str, ...] = ()
    official_source_ids: tuple[str, ...] = ()
    official_source_urls: tuple[HttpUrl, ...] = ()

class ShadowDivergence(BaseModel):
    model_config = ConfigDict(frozen=True)
    divergence_id: UUID
    reconciliation_id: UUID
    version: int = Field(ge=1)
    tenant_id: UUID
    company_tax_id: str = Field(pattern=r"^\d{14}$")
    tax_transaction_id: str
    status: Literal["MATCHED", "MATCHED_WITH_TOLERANCE", "DIVERGENT", "PENDING_HUMAN_REVIEW", "RESOLVED", "INVALIDATED"]
    divergence_type: str | None = None
    severity: Literal["REVIEW", "HIGH", "CRITICAL"] | None = None
    absolute_difference: Decimal = Field(ge=0)
    policy_version: str
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    logical_cutoff_at: datetime
    detected_at: datetime
    source_event_ids: tuple[str, ...]
    evidence: ShadowEvidence

    @model_validator(mode="after")
    def require_official_tax_provenance(self):
        if self.divergence_type in {"RULE_MISMATCH", "RATE_MISMATCH", "BASE_MISMATCH"}:
            if not (self.evidence.simulation_ids and self.evidence.rule_ids and self.evidence.memory_ids
                    and self.evidence.official_source_ids and self.evidence.official_source_urls):
                raise ValueError("tax divergence requires simulation, rule, memory and official source links")
        return self

class ShadowMetrics(BaseModel):
    total: int = Field(ge=0)
    matched: int = Field(ge=0)
    divergent: int = Field(ge=0)
    pending_review: int = Field(ge=0)
    reconciliation_rate: Decimal = Field(ge=0, le=1)
