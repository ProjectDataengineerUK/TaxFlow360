from threading import RLock
from uuid import UUID

from .readiness import ReadinessAssessment


class AssessmentNotFound(LookupError):
    pass


class InMemoryReadinessRepository:
    """Append-only repository whose every lookup requires the trusted tenant key."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._items: dict[tuple[UUID, str], tuple[ReadinessAssessment, ...]] = {}
        self._fingerprints: dict[tuple[UUID, str], ReadinessAssessment] = {}

    def add(self, assessment: ReadinessAssessment) -> ReadinessAssessment:
        key = (assessment.tenant_id, assessment.company_tax_id)
        fingerprint_key = (assessment.tenant_id, assessment.fingerprint)
        with self._lock:
            previous = self._fingerprints.get(fingerprint_key)
            if previous is not None:
                return previous
            history = self._items.get(key, ())
            self._items[key] = tuple(sorted((*history, assessment), key=lambda item: item.cutoff_at))
            self._fingerprints[fingerprint_key] = assessment
        return assessment

    def history(self, tenant_id: UUID, company_tax_id: str) -> tuple[ReadinessAssessment, ...]:
        return tuple(item for item in self._items.get((tenant_id, company_tax_id), ()) if item.status == "published")

    def latest(self, tenant_id: UUID, company_tax_id: str) -> ReadinessAssessment:
        history = self.history(tenant_id, company_tax_id)
        if not history:
            raise AssessmentNotFound("assessment not found")
        return history[-1]

    def get(self, tenant_id: UUID, company_tax_id: str, assessment_id: UUID) -> ReadinessAssessment:
        for item in self.history(tenant_id, company_tax_id):
            if item.assessment_id == assessment_id:
                return item
        raise AssessmentNotFound("assessment not found")

