from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class TaxCitation(BaseModel):
    model_config = ConfigDict(frozen=True)
    simulation_id: UUID
    rule_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    provision: str = Field(min_length=1)
    source_url: HttpUrl
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class DailyCashPoint(BaseModel):
    model_config = ConfigDict(frozen=True)
    projection_date: date
    opening_cash: Decimal
    inflow: Decimal = Field(ge=0)
    outflow: Decimal = Field(ge=0)
    tax_split_outflow: Decimal = Field(ge=0)
    closing_cash: Decimal

    @field_validator("closing_cash")
    @classmethod
    def reconcile(cls, value: Decimal, info):
        data = info.data
        expected = data["opening_cash"] + data["inflow"] - data["outflow"] - data["tax_split_outflow"]
        if value != expected:
            raise ValueError("daily cash point does not reconcile")
        return value


class ScenarioProjection(BaseModel):
    model_config = ConfigDict(frozen=True)
    scenario_id: str
    scenario_kind: Literal["baseline", "independent", "combined"]
    curve: tuple[DailyCashPoint, ...]
    minimum_balance: Decimal
    maximum_working_capital_gap: Decimal = Field(ge=0)
    days_below_minimum: int = Field(ge=0)
    tax_float_delta: Decimal


class DigitalTwinProjection(BaseModel):
    model_config = ConfigDict(frozen=True)
    projection_id: UUID
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    tenant_id: UUID
    company_tax_id: str = Field(pattern=r"^\d{11}(\d{3})?$")
    assumption_version: str
    assumption_checksum: str = Field(pattern=r"^[a-f0-9]{64}$")
    cutoff_at: datetime
    horizon_days: Literal[30, 90, 180, 365]
    model_mode: Literal["deterministic_baseline", "promoted_forecast"]
    model_version: str | None = None
    fallback_reason: str | None = None
    minimum_cash: Decimal
    scenarios: tuple[ScenarioProjection, ...]
    tax_citations: tuple[TaxCitation, ...]
    published_at: datetime


class DigitalTwinComparison(BaseModel):
    from_projection_id: UUID
    to_projection_id: UUID
    minimum_balance_delta: Decimal
    maximum_gap_delta: Decimal
    tax_float_delta: Decimal
