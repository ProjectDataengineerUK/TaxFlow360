from threading import RLock
from uuid import UUID
from .shadow_tax import ShadowDivergence, ShadowMetrics

class ShadowTaxNotFound(LookupError): pass

class InMemoryShadowTaxRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._items: dict[tuple[UUID, str], tuple[ShadowDivergence, ...]] = {}
        self._fingerprints: dict[tuple[UUID, str], ShadowDivergence] = {}

    def add(self, item: ShadowDivergence) -> ShadowDivergence:
        key = (item.tenant_id, item.fingerprint)
        with self._lock:
            if key in self._fingerprints: return self._fingerprints[key]
            history_key = (item.tenant_id, item.company_tax_id)
            self._items[history_key] = (*self._items.get(history_key, ()), item)
            self._fingerprints[key] = item
        return item

    def history(self, tenant_id: UUID, company_tax_id: str) -> tuple[ShadowDivergence, ...]:
        return self._items.get((tenant_id, company_tax_id), ())

    def get(self, tenant_id: UUID, company_tax_id: str, divergence_id: UUID) -> ShadowDivergence:
        item = next((x for x in self.history(tenant_id, company_tax_id) if x.divergence_id == divergence_id), None)
        if item is None: raise ShadowTaxNotFound("divergence not found")
        return item

    def metrics(self, tenant_id: UUID, company_tax_id: str) -> ShadowMetrics:
        latest: dict[UUID, ShadowDivergence] = {}
        for item in self.history(tenant_id, company_tax_id):
            if item.version >= latest.get(item.reconciliation_id, item).version: latest[item.reconciliation_id] = item
        values = tuple(latest.values()); total = len(values)
        matched = sum(x.status.startswith("MATCHED") for x in values)
        pending = sum(x.status == "PENDING_HUMAN_REVIEW" for x in values)
        return ShadowMetrics(total=total, matched=matched, divergent=total-matched,
            pending_review=pending, reconciliation_rate=(matched / total if total else 0))
