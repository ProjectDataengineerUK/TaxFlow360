from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data/databricks/src"))

from digital_twin_backtest import BacktestMetrics, can_promote, evaluate
from digital_twin_config import ModelGate
from digital_twin_forecast import PromotedModelAdapter, deterministic_baseline


def test_backtest_metrics_and_promotion_boundaries() -> None:
    metrics = evaluate([Decimal("100"), Decimal("200")], [Decimal("95"), Decimal("210")],
                       [Decimal("90"), Decimal("190")], [Decimal("110"), Decimal("220")])
    assert metrics.mape == Decimal("0.05")
    assert metrics.interval_coverage == Decimal("1")
    assert can_promote(metrics, Decimal("0.15"), Decimal("0.05"), Decimal("0.80"))


def test_failed_gate_and_unavailable_model_use_deterministic_fallback() -> None:
    gate = ModelGate(Decimal("0.15"), Decimal("0.05"), Decimal("0.80"))
    failed = BacktestMetrics(Decimal("0.16"), Decimal("0"), Decimal("1"), 10)
    adapter = PromotedModelAdapter("candidate", lambda history, horizon: [Decimal("99")] * horizon, failed, True)
    result = adapter.forecast([Decimal("1"), Decimal("2")], 4, gate)
    assert result.values == deterministic_baseline([Decimal("1"), Decimal("2")], 4)
    assert result.model_mode == "deterministic_baseline" and result.fallback_reason

    passing = BacktestMetrics(Decimal("0.01"), Decimal("0.01"), Decimal("1"), 10)
    unavailable = PromotedModelAdapter("candidate", lambda history, horizon: (_ for _ in ()).throw(RuntimeError()), passing, True)
    assert unavailable.forecast([Decimal("1")], 2, gate).fallback_reason == "promoted_model_unavailable"

