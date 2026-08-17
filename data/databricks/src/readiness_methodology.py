"""Strict loader for the governed Tax Readiness methodology."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from hashlib import sha256
import re
from typing import Any

import yaml

DIMENSIONS = (
    "fiscal",
    "financial",
    "erp_integrations",
    "master_data",
    "payment_methods",
    "reconciliation",
    "split_readiness",
    "working_capital",
)
_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True)
class Criterion:
    id: str
    evidence: str
    operator: str
    target: Decimal
    points: Decimal


@dataclass(frozen=True)
class Dimension:
    name: str
    weight: Decimal
    minimum_evidence: int
    criteria: tuple[Criterion, ...]


@dataclass(frozen=True)
class Methodology:
    version: str
    status: str
    dimensions: tuple[Dimension, ...]
    critical: Decimal
    attention: Decimal
    ready: Decimal
    checksum: str

    @property
    def weight_by_dimension(self) -> dict[str, Decimal]:
        return {dimension.name: dimension.weight for dimension in self.dimensions}


def _decimal(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as error:
        raise ValueError(f"{field} must be decimal-compatible") from error


def load_methodology(path: str) -> Methodology:
    """Load configuration from a workspace file or governed Unity Catalog Volume."""
    payload = Path(path).read_bytes()
    raw = yaml.safe_load(payload.decode("utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("methodology"), dict):
        raise ValueError("methodology root mapping is required")
    config = raw["methodology"]
    version = str(config.get("version", ""))
    if not _SEMVER.fullmatch(version):
        raise ValueError("methodology.version must be semantic versioning")
    status = str(config.get("status", ""))
    if status not in {"draft", "published", "retired"}:
        raise ValueError("methodology.status must be draft, published, or retired")

    dimensions_list = config.get("dimensions")
    if not isinstance(dimensions_list, list):
        raise ValueError("methodology.dimensions must be a list")
    dimensions_config = {item.get("id"): item for item in dimensions_list if isinstance(item, dict)}
    if len(dimensions_config) != len(dimensions_list) or set(dimensions_config) != set(DIMENSIONS):
        raise ValueError(f"methodology must contain exactly these dimensions: {', '.join(DIMENSIONS)}")
    dimensions: list[Dimension] = []
    for name in DIMENSIONS:
        item = dimensions_config[name]
        if not isinstance(item, dict):
            raise ValueError(f"methodology.dimensions.{name} must be a mapping")
        weight = _decimal(item.get("weight"), f"dimensions.{name}.weight")
        minimum_evidence = item.get("minimum_evidence")
        if weight <= 0 or not isinstance(minimum_evidence, int) or minimum_evidence < 1:
            raise ValueError(f"dimension {name} requires positive weight and minimum_evidence")
        criteria_config = item.get("criteria")
        if not isinstance(criteria_config, list) or not criteria_config:
            raise ValueError(f"dimension {name} requires criteria")
        criteria: list[Criterion] = []
        criterion_ids: set[str] = set()
        evidence_ids: set[str] = set()
        for criterion in criteria_config:
            if not isinstance(criterion, dict):
                raise ValueError(f"dimension {name} criterion must be a mapping")
            criterion_id = str(criterion.get("id", ""))
            evidence_id = str(criterion.get("evidence", ""))
            operator = str(criterion.get("operator", ""))
            if not criterion_id or criterion_id in criterion_ids or not evidence_id or evidence_id in evidence_ids:
                raise ValueError(f"dimension {name} requires unique criterion and evidence IDs")
            if operator not in {"greater_than_or_equal", "less_than_or_equal", "equal"}:
                raise ValueError(f"criterion {criterion_id} declares unsupported operator {operator}")
            target = _decimal(criterion.get("target"), f"criteria.{criterion_id}.target")
            points = _decimal(criterion.get("points"), f"criteria.{criterion_id}.points")
            if points <= 0:
                raise ValueError(f"criterion {criterion_id} points must be positive")
            criteria.append(Criterion(criterion_id, evidence_id, operator, target, points))
            criterion_ids.add(criterion_id)
            evidence_ids.add(evidence_id)
        if sum((criterion.points for criterion in criteria), Decimal(0)) != Decimal("100"):
            raise ValueError(f"dimension {name} criterion points must sum exactly to 100")
        dimensions.append(Dimension(name, weight, minimum_evidence, tuple(criteria)))
    if sum((item.weight for item in dimensions), Decimal(0)) != Decimal("1"):
        raise ValueError("dimension weights must sum exactly to 1")

    thresholds = config.get("thresholds", {})
    critical = _decimal(thresholds.get("critical"), "thresholds.critical")
    attention = _decimal(thresholds.get("attention"), "thresholds.attention")
    ready = _decimal(thresholds.get("ready"), "thresholds.ready")
    if not (Decimal(0) <= critical < attention < ready <= Decimal(100)):
        raise ValueError("thresholds must satisfy 0 <= critical < attention < ready <= 100")
    return Methodology(version, status, tuple(dimensions), critical, attention, ready, sha256(payload).hexdigest())
