import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class DataContractTests(unittest.TestCase):
    def test_avro_event_has_required_identity_fields(self) -> None:
        schema = json.loads((ROOT / "contracts/events/tax-transaction.avsc").read_text(encoding="utf-8"))
        field_names = {field["name"] for field in schema["fields"]}
        required = {
            "event_id",
            "tax_transaction_id",
            "tenant_id",
            "company_tax_id",
            "source_system",
            "source_event_id",
            "schema_version",
            "correlation_id",
            "ingested_at",
        }
        self.assertTrue(required.issubset(field_names))

    def test_avro_defaults_follow_required_fields(self) -> None:
        schema = json.loads((ROOT / "contracts/events/tax-transaction.avsc").read_text(encoding="utf-8"))
        default_seen = False
        for field in schema["fields"]:
            if "default" in field:
                default_seen = True
            self.assertFalse(default_seen and "default" not in field)

    def test_odcs_contract_declares_backward_compatibility(self) -> None:
        contract = (ROOT / "contracts/data/tax-transaction.contract.yaml").read_text(encoding="utf-8")
        self.assertRegex(contract, r"(?m)^\s*compatibility:\s*backward\s*$")
        for field_name in ("event_id", "tax_transaction_id", "tenant_id", "company_tax_id", "operation_amount"):
            self.assertIsNotNone(re.search(rf"(?m)^\s*- name:\s*{field_name}\s*$", contract))

    def test_openapi_has_tenant_safe_operations(self) -> None:
        api = (ROOT / "contracts/api/openapi.yaml").read_text(encoding="utf-8")
        self.assertIn("operationId: createTransaction", api)
        self.assertIn("Idempotency-Key", api)
        self.assertIn("securitySchemes:", api)


if __name__ == "__main__":
    unittest.main()
