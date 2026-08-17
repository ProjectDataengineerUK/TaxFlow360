from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "data/databricks/src"))

from digital_twin_reference import CashMovement, liquidity_indicators, project_day, project_ledger


def test_daily_ledger_reconciles_exact_decimal_and_running_balance() -> None:
    start = date(2027, 1, 1)
    movements = tuple(CashMovement(start + timedelta(days=index), Decimal("100.10"), Decimal("40.05"), Decimal("10.01"))
                      for index in range(3))
    ledger = project_ledger(Decimal("1000.00"), movements)
    assert ledger[0].closing_cash == Decimal("1050.04")
    assert ledger[1].opening_cash == ledger[0].closing_cash
    assert ledger[-1].closing_cash == Decimal("1150.12")
    assert all(day.opening_cash + day.inflow - day.outflow - day.tax_split_outflow == day.closing_cash for day in ledger)


def test_liquidity_gap_days_and_tax_float() -> None:
    start = date(2027, 1, 1)
    ledger = project_ledger(Decimal("100"), (
        CashMovement(start, Decimal("0"), Decimal("30"), Decimal("10")),
        CashMovement(start + timedelta(days=1), Decimal("5"), Decimal("20"), Decimal("5")),
    ))
    indicators = liquidity_indicators(ledger, Decimal("80"), baseline_tax_split=Decimal("5"))
    assert indicators.minimum_balance == Decimal("40.00")
    assert indicators.maximum_working_capital_gap == Decimal("40.00")
    assert indicators.days_below_minimum == 2
    assert indicators.tax_float_delta == Decimal("10.00")


def test_project_day_uses_half_even_money_scale() -> None:
    result = project_day(date(2027, 1, 1), Decimal("10.005"), Decimal("1.005"), Decimal("0"), Decimal("0"))
    assert result.opening_cash == Decimal("10.00") and result.inflow == Decimal("1.00")

