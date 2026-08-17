import csv
import io
import sys
import unittest
from pathlib import Path
from uuid import UUID


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services/ingestion-service/src"))


class IngestionFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            from taxflow_ingestion.api import _published, _quarantine, _seen
        except (ImportError, RuntimeError) as exc:
            self.skipTest(str(exc))
        _published.clear()
        _quarantine.clear()
        _seen.clear()

    @staticmethod
    def csv_payload(rows: list[dict[str, str]]) -> bytes:
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return stream.getvalue().encode()

    def test_valid_invalid_and_duplicate_records_are_accounted_for(self) -> None:
        try:
            from taxflow_ingestion.api import ingest
        except (ImportError, RuntimeError) as exc:
            self.skipTest(str(exc))
        tenant_id = UUID("00000000-0000-0000-0000-000000000001")
        valid = {
            "tax_transaction_id": "TX-1",
            "source_event_id": "EV-1",
            "company_tax_id": "12345678000199",
            "occurred_at": "2027-01-01T12:00:00Z",
            "operation_amount": "100.00",
            "currency": "BRL",
        }
        invalid = {**valid, "tax_transaction_id": "TX-2", "source_event_id": "EV-2", "operation_amount": "invalid"}
        first = ingest(self.csv_payload([valid, invalid]), "input.csv", tenant_id, "synthetic")
        second = ingest(self.csv_payload([valid]), "input.csv", tenant_id, "synthetic")
        self.assertEqual((first.accepted, first.quarantined, first.duplicate), (1, 1, 0))
        self.assertEqual((second.accepted, second.quarantined, second.duplicate), (0, 0, 1))

    def test_same_source_event_is_independent_between_tenants(self) -> None:
        from taxflow_ingestion.api import ingest
        row = {"tax_transaction_id": "TX-1", "company_tax_id": "12345678000199",
               "source_event_id": "EV-1", "occurred_at": "2027-01-01T12:00:00Z",
               "operation_amount": "100.00", "currency": "BRL"}
        first = ingest(self.csv_payload([row]), "input.csv", UUID(int=1), "synthetic")
        second = ingest(self.csv_payload([row]), "input.csv", UUID(int=2), "synthetic")
        self.assertEqual((first.accepted, second.accepted), (1, 1))


if __name__ == "__main__":
    unittest.main()
