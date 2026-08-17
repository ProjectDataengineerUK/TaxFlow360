"""Strict loader for immutable Digital Twin assumption snapshots."""

from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import re
from typing import Any

import yaml

_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True)
class ModelGate:
    maximum_mape: Decimal
    maximum_absolute_bias: Decimal
    minimum_interval_coverage: Decimal


@dataclass(frozen=True)
class Stress:
    stress_id: str
    driver: str
    operation: str
    factor: Decimal
    combined: bool
    stress_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DigitalTwinConfig:
    version: str
    checksum: str
    horizons_days: tuple[int, ...]
    minimum_history_days: int
    minimum_cash: Decimal
    random_seed: int
    model_gate: ModelGate
    stresses: tuple[Stress, ...]


def _decimal(value: Any, field: str) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as error:
        raise ValueError(f"{field} must be decimal-compatible") from error


def load_config(path: str) -> DigitalTwinConfig:
    payload = Path(path).read_bytes()
    document = yaml.safe_load(payload.decode("utf-8"))
    root = document.get("digital_twin") if isinstance(document, dict) else None
    if not isinstance(root, dict) or not _SEMVER.fullmatch(str(root.get("version", ""))):
        raise ValueError("digital_twin.version must be semantic versioning")
    if root.get("status") not in {"draft", "approved", "retired"} or root.get("currency") != "BRL":
        raise ValueError("status and BRL currency are required")
    if root.get("rounding") != {"scale": 2, "mode": "HALF_EVEN"}:
        raise ValueError("rounding must be scale 2 HALF_EVEN")
    horizons = tuple(root.get("horizons_days", ()))
    if not horizons or any(not isinstance(value, int) or value < 1 or value > 3650 for value in horizons) or len(set(horizons)) != len(horizons):
        raise ValueError("horizons_days must contain unique positive integers")
    history = root.get("minimum_history_days")
    if not isinstance(history, int) or history < 1:
        raise ValueError("minimum_history_days must be positive")
    minimum_cash = root.get("minimum_cash", {})
    if minimum_cash.get("mode") != "fixed" or _decimal(minimum_cash.get("amount"), "minimum_cash.amount") < 0:
        raise ValueError("minimum_cash must be a non-negative fixed Decimal")
    gate_data = root.get("model_gate", {})
    gate = ModelGate(_decimal(gate_data.get("maximum_mape"), "model_gate.maximum_mape"),
                     _decimal(gate_data.get("maximum_absolute_bias"), "model_gate.maximum_absolute_bias"),
                     _decimal(gate_data.get("minimum_interval_coverage"), "model_gate.minimum_interval_coverage"))
    if not (Decimal(0) <= gate.maximum_mape <= 1 and Decimal(0) <= gate.maximum_absolute_bias <= 1
            and Decimal(0) <= gate.minimum_interval_coverage <= 1):
        raise ValueError("model gate values must be ratios in [0,1]")
    stresses: list[Stress] = []
    seen: set[str] = set()
    stress_groups = root.get("stresses", {})
    if not isinstance(stress_groups, dict):
        raise ValueError("stresses must contain independent and combined lists")
    for item in stress_groups.get("independent", []):
        stress_id = str(item.get("id", ""))
        operation = str(item.get("operation", ""))
        if not stress_id or stress_id in seen or operation not in {"multiply", "shift_days", "add_rate"}:
            raise ValueError("stress IDs must be unique and operations supported")
        parameter = item.get("factor", item.get("days", item.get("value")))
        stresses.append(Stress(stress_id, str(item.get("driver", "")), operation,
                               _decimal(parameter, f"stresses.{stress_id}.parameter"), False))
        seen.add(stress_id)
    independent_ids = set(seen)
    for item in stress_groups.get("combined", []):
        stress_id = str(item.get("id", ""))
        members = tuple(item.get("stress_ids", ()))
        if not stress_id or stress_id in seen or len(members) < 2 or not set(members) <= independent_ids:
            raise ValueError("combined stress must reference at least two declared independent stresses")
        stresses.append(Stress(stress_id, "combined", "combine", Decimal(1), True, members))
        seen.add(stress_id)
    independent = sum(not stress.combined for stress in stresses)
    combined = sum(stress.combined for stress in stresses)
    if independent < 6 or combined < 3:
        raise ValueError("configuration requires at least six independent and three combined stresses")
    seed = root.get("random_seed", 360)
    if not isinstance(seed, int):
        raise ValueError("random_seed must be an integer")
    return DigitalTwinConfig(str(root["version"]), sha256(payload).hexdigest(), horizons, history,
                             _decimal(minimum_cash["amount"], "minimum_cash.amount"), seed, gate, tuple(stresses))
