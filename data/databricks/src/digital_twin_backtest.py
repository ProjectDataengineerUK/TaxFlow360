"""Decimal backtest metrics and the only model-promotion gate."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


@dataclass(frozen=True)
class BacktestMetrics:
    mape: Decimal
    absolute_bias: Decimal
    interval_coverage: Decimal
    observations: int


def evaluate(actual: Iterable[Decimal], predicted: Iterable[Decimal],
             lower: Iterable[Decimal], upper: Iterable[Decimal]) -> BacktestMetrics:
    rows = tuple(zip(actual, predicted, lower, upper, strict=True))
    if not rows:
        raise ValueError("backtest requires observations")
    nonzero = tuple(row for row in rows if row[0] != 0)
    if not nonzero:
        raise ValueError("MAPE requires at least one non-zero actual")
    mape = sum((abs(actual_value - estimate) / abs(actual_value) for actual_value, estimate, _, _ in nonzero), Decimal(0)) / len(nonzero)
    actual_total = sum((row[0] for row in rows), Decimal(0))
    bias_denominator = sum((abs(row[0]) for row in rows), Decimal(0))
    bias = abs(sum((row[1] - row[0] for row in rows), Decimal(0))) / bias_denominator if bias_denominator else abs(actual_total)
    coverage = Decimal(sum(low <= value <= high for value, _, low, high in rows)) / Decimal(len(rows))
    return BacktestMetrics(mape, bias, coverage, len(rows))


def can_promote(metrics: BacktestMetrics, maximum_mape: Decimal,
                maximum_absolute_bias: Decimal = Decimal("0.05"),
                minimum_interval_coverage: Decimal = Decimal("0.80")) -> bool:
    return (metrics.mape <= maximum_mape and metrics.absolute_bias <= maximum_absolute_bias
            and metrics.interval_coverage >= minimum_interval_coverage)
