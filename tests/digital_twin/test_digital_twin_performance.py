from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "databricks" / "src"))

from digital_twin_reference import project_day  # noqa: E402


def test_100k_deterministic_cash_movements_complete_within_wave_budget() -> None:
    started = time.perf_counter()
    day = date(2027, 1, 1)
    balance = Decimal("100000.00")
    checksum = Decimal(0)
    for index in range(100_000):
        projected = project_day(day + timedelta(days=index), balance, Decimal("100.00"),
                                Decimal("40.00"), Decimal("8.80"))
        balance = projected.closing_cash
        checksum += projected.tax_split_outflow
    elapsed = time.perf_counter() - started
    assert checksum == Decimal("880000.00")
    assert elapsed <= 900, f"100k projection exceeded 15-minute acceptance budget: {elapsed:.2f}s"
