from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "databricks" / "src"))

from tax_rule_catalog import load_catalog  # noqa: E402


def catalog():
    return load_catalog(str(ROOT / "config" / "tax-rule-catalog.yaml"),
                        str(ROOT / "config" / "official-source-authorities.yaml"))


def reference(amount: Decimal, rates: dict[str, Decimal]) -> dict[str, Decimal]:
    return {component: (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
            for component, rate in rates.items()}


def test_catalog_matches_reference_decimal_semantics_and_sources() -> None:
    snapshot = catalog()
    effective_at = datetime(2027, 1, 1, tzinfo=timezone.utc)
    for scenario in ("reform", "split"):
        rules = snapshot.select(scenario, effective_at)
        rates = {rule.component: rule.rate for rule in rules}
        for amount in (Decimal("0.01"), Decimal("1.25"), Decimal("99.99"), Decimal("1000000.05")):
            assert snapshot.calculate(amount, scenario, effective_at) == reference(amount, rates)
        assert all(rule.sources for rule in rules)
        assert all(source.source_url.startswith("https://") and len(source.content_sha256) == 64
                   for rule in rules for source in rule.sources)


def test_snapshot_is_deterministic_and_temporal_boundaries_are_exclusive() -> None:
    first = catalog()
    second = catalog()
    assert first == second
    current = first.select("current", datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
    assert [rule.rule_id for rule in current] == ["current-general-2026"]
    try:
        first.select("current", datetime(2027, 1, 1, tzinfo=timezone.utc))
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("valid_until must be exclusive")
