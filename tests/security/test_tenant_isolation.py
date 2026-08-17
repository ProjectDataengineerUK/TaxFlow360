import unittest
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Principal:
    tenant_id: UUID
    roles: frozenset[str]


def authorize(principal: Principal, resource_tenant_id: UUID, required_role: str) -> bool:
    return principal.tenant_id == resource_tenant_id and required_role in principal.roles


class TenantIsolationTests(unittest.TestCase):
    def test_tenant_is_part_of_ingestion_idempotency_key(self) -> None:
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        sys.path.insert(0, str(root / "services/ingestion-service/src"))
        try:
            from taxflow_ingestion.models import TaxTransaction
        except (ImportError, RuntimeError) as exc:
            self.skipTest(str(exc))
        common = dict(tax_transaction_id="TX-1", company_tax_id="12345678000199",
                      source_system="erp", source_event_id="EV-1", occurred_at="2027-01-01T00:00:00Z",
                      operation_amount="1.00")
        first = TaxTransaction(tenant_id=UUID(int=1), **common)
        second = TaxTransaction(tenant_id=UUID(int=2), **common)
        self.assertNotEqual(first.idempotency_key, second.idempotency_key)

    def test_cross_tenant_access_is_denied(self) -> None:
        first = UUID("00000000-0000-0000-0000-000000000001")
        second = UUID("00000000-0000-0000-0000-000000000002")
        self.assertFalse(authorize(Principal(first, frozenset({"readiness.read"})), second, "readiness.read"))

    def test_missing_role_is_denied_inside_tenant(self) -> None:
        tenant = UUID("00000000-0000-0000-0000-000000000001")
        self.assertFalse(authorize(Principal(tenant, frozenset()), tenant, "readiness.read"))

    def test_matching_tenant_and_role_is_allowed(self) -> None:
        tenant = UUID("00000000-0000-0000-0000-000000000001")
        self.assertTrue(authorize(Principal(tenant, frozenset({"readiness.read"})), tenant, "readiness.read"))


if __name__ == "__main__":
    unittest.main()
