from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data/databricks/src"))

from digital_twin_reference import CashMovement, StressScenario, apply_stress, run_stresses

INDEPENDENT = (
    StressScenario("revenue_down_10", revenue_factor=Decimal("0.90")),
    StressScenario("receivables_delay_15d", collection_delay_days=15),
    StressScenario("costs_up_08", expense_factor=Decimal("1.08")),
    StressScenario("payables_accelerate_10d", payable_acceleration_days=10),
    StressScenario("tax_split_up_05", tax_split_factor=Decimal("1.05")),
    StressScenario("interest_up_200bps", interest_rate_addition=Decimal("0.0200")),
)
COMBINED = (
    StressScenario("demand_and_collection_shock", revenue_factor=Decimal("0.90"), collection_delay_days=15),
    StressScenario("margin_and_tax_shock", expense_factor=Decimal("1.08"), tax_split_factor=Decimal("1.05")),
    StressScenario("severe_liquidity_shock", revenue_factor=Decimal("0.90"), expense_factor=Decimal("1.08"),
                   tax_split_factor=Decimal("1.05"), collection_delay_days=15,
                   payable_acceleration_days=10, interest_rate_addition=Decimal("0.0200")),
)


def movements() -> tuple[CashMovement, ...]:
    start = date(2027, 1, 1)
    return tuple(CashMovement(start + timedelta(days=index), Decimal("100"), Decimal("60"), Decimal("10"))
                 for index in range(30))


@pytest.mark.parametrize("scenario", INDEPENDENT)
def test_six_independent_stresses_are_deterministic(scenario: StressScenario) -> None:
    first = apply_stress(movements(), scenario)
    assert first == apply_stress(movements(), scenario)
    assert first != movements()


@pytest.mark.parametrize("scenario", COMBINED)
def test_three_combined_stresses_are_deterministic(scenario: StressScenario) -> None:
    results = run_stresses(Decimal("1000"), movements(), (scenario,))
    assert tuple(results) == (scenario.scenario_id,)
    assert len(results[scenario.scenario_id]) == 30

