from collections.abc import Callable
from threading import Lock
from uuid import UUID, uuid4

from fastapi import FastAPI, File, Header, HTTPException, UploadFile, status
from pydantic import ValidationError

from .models import IngestionResult, QuarantineRecord, TaxTransaction, canonical_from_mapping
from .parsers import parser_for

app = FastAPI(title="TaxFlow Ingestion API", version="0.1.0")
_lock = Lock()
_seen: set[str] = set()
_published: list[TaxTransaction] = []
_quarantine: list[QuarantineRecord] = []


def ingest(content: bytes, filename: str, tenant_id: UUID, source_system: str,
           publish: Callable[[TaxTransaction], None] = _published.append) -> IngestionResult:
    correlation_id = uuid4()
    accepted = duplicates = 0
    event_ids: list[UUID] = []
    try:
        records = parser_for(filename).parse(content)
        for row_number, record in enumerate(records, start=2):
            try:
                transaction = canonical_from_mapping(record, tenant_id=tenant_id, source_system=source_system)
                with _lock:
                    if transaction.idempotency_key in _seen:
                        duplicates += 1
                        continue
                    publish(transaction)
                    _seen.add(transaction.idempotency_key)
                accepted += 1
                event_ids.append(transaction.event_id)
            except (KeyError, TypeError, ValueError, ValidationError) as exc:
                _quarantine.append(QuarantineRecord(correlation_id=correlation_id, tenant_id=tenant_id,
                    source_name=filename, error_code="INVALID_RECORD", detail=str(exc)[:1000], row_number=row_number))
    except (ValueError, UnicodeError, RuntimeError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    quarantined = sum(item.correlation_id == correlation_id for item in _quarantine)
    return IngestionResult(accepted=accepted, quarantined=quarantined, duplicate=duplicates,
                           correlation_id=correlation_id, event_ids=event_ids)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ingestions", response_model=IngestionResult, status_code=status.HTTP_202_ACCEPTED)
async def upload(file: UploadFile = File(...), x_tenant_id: UUID = Header(...),
                 x_source_system: str = Header(..., min_length=1)) -> IngestionResult:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="file must not be empty")
    return ingest(content, file.filename or "upload", x_tenant_id, x_source_system)


def run() -> None:
    import uvicorn
    uvicorn.run("taxflow_ingestion.api:app", host="0.0.0.0", port=8080)
