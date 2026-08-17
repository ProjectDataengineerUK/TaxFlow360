from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "databricks" / "src"))

from digital_twin_reference import CashMovement, project_ledger  # noqa: E402


def spark_compatible(opening: Decimal, movements: tuple[CashMovement, ...]):
    balance = opening.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    result = []
    for movement in movements:
        inflow = movement.inflow.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        outflow = movement.outflow.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        split = movement.tax_split_outflow.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        closing = (balance + inflow - outflow - split).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        result.append((movement.projection_date, balance, inflow, outflow, split, closing))
        balance = closing
    return tuple(result)


def test_reference_and_spark_compatible_daily_semantics_are_exact() -> None:
    start = date(2027, 1, 1)
    movements = tuple(CashMovement(start + timedelta(days=index), Decimal("100.005") + index,
                                   Decimal("40.005"), Decimal("8.805")) for index in range(120))
    reference = project_ledger(Decimal("100000.005"), movements)
    expected = spark_compatible(Decimal("100000.005"), movements)
    assert tuple((row.projection_date, row.opening_cash, row.inflow, row.outflow,
                  row.tax_split_outflow, row.closing_cash) for row in reference) == expected
    assert all(expected[index][1] == expected[index - 1][-1] for index in range(1, len(expected)))
