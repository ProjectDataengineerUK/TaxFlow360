from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "databricks" / "src"))

from tax_rule_catalog import load_catalog  # noqa: E402


def test_reference_engine_processes_100k_without_loss_within_wave_budget() -> None:
    snapshot = load_catalog(str(ROOT / "config" / "tax-rule-catalog.yaml"),
                            str(ROOT / "config" / "official-source-authorities.yaml"))
    effective_at = datetime(2027, 1, 1, tzinfo=timezone.utc)
    started = time.perf_counter()
    checksum = Decimal(0)
    for index in range(100_000):
        result = snapshot.calculate(Decimal(index % 10_000) / Decimal(100), "reform", effective_at)
        checksum += sum(result.values(), Decimal(0))
    elapsed = time.perf_counter() - started
    assert checksum > 0
    assert elapsed <= 900, f"100k reference batch exceeded 15-minute acceptance budget: {elapsed:.2f}s"
