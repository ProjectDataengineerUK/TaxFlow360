"""Deterministic forecast floor plus an injected, governed MLflow adapter."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Callable, Sequence

from digital_twin_backtest import BacktestMetrics, can_promote
from digital_twin_config import ModelGate

CENT = Decimal("0.01")


@dataclass(frozen=True)
class ForecastResult:
    values: tuple[Decimal, ...]
    model_mode: str
    model_version: str | None
    fallback_reason: str | None


def deterministic_baseline(history: Sequence[Decimal], horizon_days: int, season_days: int = 7) -> tuple[Decimal, ...]:
    if horizon_days < 1 or not history:
        raise ValueError("history and a positive horizon are required")
    window = tuple(history[-min(len(history), season_days):])
    return tuple(window[index % len(window)].quantize(CENT, rounding=ROUND_HALF_EVEN) for index in range(horizon_days))


class PromotedModelAdapter:
    """Loads only a caller-verified model; this module never performs registry/network lookup."""

    def __init__(self, model_version: str, predict: Callable[[Sequence[Decimal], int], Sequence[Decimal]],
                 metrics: BacktestMetrics, promoted: bool) -> None:
        self.model_version = model_version
        self._predict = predict
        self.metrics = metrics
        self.promoted = promoted

    def forecast(self, history: Sequence[Decimal], horizon_days: int, gate: ModelGate) -> ForecastResult:
        if not self.promoted or not can_promote(self.metrics, gate.maximum_mape,
                                                gate.maximum_absolute_bias, gate.minimum_interval_coverage):
            return ForecastResult(deterministic_baseline(history, horizon_days), "deterministic_baseline", None,
                                  "model_not_promoted_or_backtest_gate_failed")
        try:
            values = tuple(Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_EVEN)
                           for value in self._predict(history, horizon_days))
            if len(values) != horizon_days:
                raise ValueError("model output length mismatch")
            return ForecastResult(values, "promoted_mlflow", self.model_version, None)
        except Exception:
            return ForecastResult(deterministic_baseline(history, horizon_days), "deterministic_baseline", None,
                                  "promoted_model_unavailable")
