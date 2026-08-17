from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaxTransaction(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    tax_transaction_id: str = Field(min_length=1, max_length=128)
    tenant_id: UUID
    company_tax_id: str = Field(pattern=r"^\d{11}(\d{3})?$")
    source_system: str = Field(min_length=1, max_length=64)
    source_event_id: str = Field(min_length=1, max_length=128)
    occurred_at: datetime
    operation_amount: Decimal = Field(ge=Decimal("0"), max_digits=20, decimal_places=2)
    currency: Literal["BRL"] = "BRL"
    correlation_id: UUID = Field(default_factory=uuid4)
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    document_type: str | None = Field(default=None, max_length=64)
    document_key: str | None = Field(default=None, max_length=128)
    schema_version: str = Field(default="1.0.0", pattern=r"^[1-9]\d*\.\d+\.\d+$")

    @field_validator("occurred_at", "ingested_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone")
        return value.astimezone(timezone.utc)

    @property
    def idempotency_key(self) -> str:
        return f"{self.tenant_id}:{self.source_system}:{self.source_event_id}"


class QuarantineRecord(BaseModel):
    model_config = ConfigDict(frozen=True)
    correlation_id: UUID
    tenant_id: UUID
    source_name: str
    error_code: str
    detail: str
    row_number: int | None = None


class IngestionResult(BaseModel):
    accepted: int
    quarantined: int
    duplicate: int
    correlation_id: UUID
    event_ids: list[UUID]


def canonical_from_mapping(data: dict[str, Any], *, tenant_id: UUID, source_system: str) -> TaxTransaction:
    normalized = {str(key).strip().lower(): value for key, value in data.items()}
    return TaxTransaction(
        tax_transaction_id=str(normalized["tax_transaction_id"]),
        tenant_id=tenant_id,
        company_tax_id=str(normalized["company_tax_id"]),
        source_system=source_system,
        source_event_id=str(normalized["source_event_id"]),
        occurred_at=normalized["occurred_at"],
        operation_amount=normalized["operation_amount"],
        currency=str(normalized.get("currency", "BRL")).upper(),
        correlation_id=normalized.get("correlation_id", uuid4()),
        ingested_at=normalized.get("ingested_at", datetime.now(timezone.utc)),
        document_type=normalized.get("document_type") or None,
        document_key=normalized.get("document_key") or None,
        schema_version=str(normalized.get("schema_version", "1.0.0")),
    )
