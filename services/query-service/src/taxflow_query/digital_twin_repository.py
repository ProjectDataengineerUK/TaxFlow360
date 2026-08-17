from threading import RLock
from uuid import UUID

from .digital_twin import DigitalTwinProjection


class DigitalTwinNotFound(LookupError):
    pass


class InMemoryDigitalTwinRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self._items: dict[tuple[UUID, str], tuple[DigitalTwinProjection, ...]] = {}
        self._fingerprints: dict[tuple[UUID, str], DigitalTwinProjection] = {}

    def add(self, item: DigitalTwinProjection) -> DigitalTwinProjection:
        key = (item.tenant_id, item.fingerprint)
        with self._lock:
            if key in self._fingerprints:
                return self._fingerprints[key]
            history_key = (item.tenant_id, item.company_tax_id)
            history = self._items.get(history_key, ())
            self._items[history_key] = tuple(sorted((*history, item), key=lambda value: value.published_at))
            self._fingerprints[key] = item
        return item

    def history(self, tenant_id: UUID, company_tax_id: str) -> tuple[DigitalTwinProjection, ...]:
        return self._items.get((tenant_id, company_tax_id), ())

    def latest(self, tenant_id: UUID, company_tax_id: str) -> DigitalTwinProjection:
        history = self.history(tenant_id, company_tax_id)
        if not history:
            raise DigitalTwinNotFound("projection not found")
        return history[-1]

    def get(self, tenant_id: UUID, company_tax_id: str, projection_id: UUID) -> DigitalTwinProjection:
        for item in self.history(tenant_id, company_tax_id):
            if item.projection_id == projection_id:
                return item
        raise DigitalTwinNotFound("projection not found")

