import unittest
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ReconciliationInput:
    tax_transaction_id: str
    invoice: Decimal
    ledger: Decimal
    payment: Decimal
    split: Decimal


def reconcile(item: ReconciliationInput) -> tuple[bool, Decimal]:
    values = (item.invoice, item.ledger, item.payment, item.split)
    return len(set(values)) == 1, max(values) - min(values)


class ReconciliationTests(unittest.TestCase):
    def test_four_equal_points_reconcile(self) -> None:
        matched, difference = reconcile(ReconciliationInput("TX-1", *(Decimal("100.00"),) * 4))
        self.assertTrue(matched)
        self.assertEqual(difference, Decimal("0.00"))

    def test_divergence_is_quantified(self) -> None:
        matched, difference = reconcile(
            ReconciliationInput("TX-2", Decimal("100.00"), Decimal("100.00"), Decimal("99.90"), Decimal("100.00"))
        )
        self.assertFalse(matched)
        self.assertEqual(difference, Decimal("0.10"))


if __name__ == "__main__":
    unittest.main()

