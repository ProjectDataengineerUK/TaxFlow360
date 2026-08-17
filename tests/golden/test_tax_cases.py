import unittest
from datetime import UTC, datetime
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = ROOT / "tests" / "golden" / "tax-simulation-cases.yaml"
CATALOG_PATH = ROOT / "config" / "tax-rule-catalog.yaml"


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)


class GoldenTaxCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.vectors = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
        cls.catalog = yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))["catalog"]
        cls.rules = {rule["id"]: rule for rule in cls.catalog["rules"]}

    def test_at_least_fifty_unique_synthetic_cases(self) -> None:
        cases = self.vectors["cases"]
        self.assertGreaterEqual(len(cases), 50)
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        self.assertTrue(self.vectors["synthetic"])

    def test_catalog_and_vectors_share_frozen_version(self) -> None:
        self.assertEqual(self.vectors["rule_set_version"], self.catalog["version"])
        self.assertEqual(self.vectors["rounding"], self.catalog["rounding"])

    def test_every_expected_component_is_exact_and_traceable(self) -> None:
        for case in self.vectors["cases"]:
            base = Decimal(case["operation_amount"])
            expected = case["expected"]
            component_total = Decimal("0")
            for component in expected["components"]:
                rule = self.rules[component["rule_id"]]
                calculated = money(base * Decimal(str(rule["rate"])))
                self.assertEqual(calculated, Decimal(component["amount"]), case["id"])
                self.assertEqual(component["rate"], str(rule["rate"]), case["id"])
                self.assertTrue(component["source_ids"], case["id"])
                self.assertEqual(
                    set(component["source_ids"]),
                    {source["source_id"] for source in rule["sources"]},
                    case["id"],
                )
                component_total += calculated
            self.assertEqual(component_total, Decimal(expected["total_tax"]), case["id"])

    def test_scenario_cash_and_split_invariants(self) -> None:
        for case in self.vectors["cases"]:
            base = Decimal(case["operation_amount"])
            expected = case["expected"]
            authority = Decimal(expected["authority_amount"])
            company = Decimal(expected["company_amount"])
            if case["scenario"] == "split":
                self.assertEqual(authority, Decimal(expected["total_tax"]), case["id"])
                self.assertEqual(company + authority, base, case["id"])
            else:
                self.assertEqual(authority, Decimal("0.00"), case["id"])
                self.assertEqual(company, base, case["id"])

    def test_rules_are_approved_effective_and_four_eyes(self) -> None:
        for case in self.vectors["cases"]:
            instant = datetime.fromisoformat(case["occurred_at"].replace("Z", "+00:00")).astimezone(UTC)
            for component in case["expected"]["components"]:
                rule = self.rules[component["rule_id"]]
                start = datetime.fromisoformat(rule["valid_from"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(rule["valid_until"].replace("Z", "+00:00")) if rule["valid_until"] else None
                self.assertEqual(rule["status"], "approved")
                self.assertNotEqual(rule["author_id"], rule["approver_id"])
                self.assertGreaterEqual(instant, start)
                self.assertTrue(end is None or instant < end)


if __name__ == "__main__":
    unittest.main()
