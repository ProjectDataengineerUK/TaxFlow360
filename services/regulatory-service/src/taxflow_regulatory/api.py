from datetime import datetime
from uuid import UUID
from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel
from .change_workflow import ChangeWorkflow
from .models import ChangeRequest,CopilotAnswer
from .repository import ChangeNotFound,InMemoryChangeRepository

app=FastAPI(title="TaxFlow Regulatory API",version="0.1.0")
repository=InMemoryChangeRepository(); workflow=ChangeWorkflow()
class TransitionRequest(BaseModel): justification:str
class AnswerRequest(BaseModel): question:str; cutoff_at:datetime; authority_ids:tuple[str,...]; document_types:tuple[str,...]; jurisdiction:str="BR"

@app.get("/health")
def health():return {"status":"ok"}
@app.post("/v1/regulatory/answer",response_model=CopilotAnswer)
def answer(body:AnswerRequest,x_tenant_id:UUID=Header(...)):
    del x_tenant_id
    if not body.authority_ids or not body.document_types:
        raise HTTPException(422,"authority and document type filters are required")
    return CopilotAnswer(disposition="refused",reason="official evidence index is not configured in this environment",cutoff_at=body.cutoff_at,policy_version="1.0.0",model_version="unavailable")
@app.get("/v1/regulatory/changes/{change_id}",response_model=list[ChangeRequest])
def history(change_id:UUID,x_tenant_id:UUID=Header(...)):
    try:return repository.history(x_tenant_id,change_id)
    except ChangeNotFound as exc:raise HTTPException(404,"change request not found") from exc
@app.post("/v1/regulatory/changes/{change_id}/submit",response_model=ChangeRequest)
def submit(change_id:UUID,body:TransitionRequest,x_tenant_id:UUID=Header(...),x_actor_id:str=Header(...),x_roles:str=Header(...)):
    try:current=repository.latest(x_tenant_id,change_id)
    except ChangeNotFound as exc:raise HTTPException(404,"change request not found") from exc
    try:return repository.append(workflow.submit(current,x_actor_id,frozenset(x_roles.split(",")),body.justification))
    except PermissionError as exc:raise HTTPException(403,"transition denied") from exc
@app.post("/v1/regulatory/changes/{change_id}/approve",response_model=ChangeRequest)
def approve(change_id:UUID,x_tenant_id:UUID=Header(...),x_actor_id:str=Header(...),x_roles:str=Header(...)):
    try:current=repository.latest(x_tenant_id,change_id)
    except ChangeNotFound as exc:raise HTTPException(404,"change request not found") from exc
    try:return repository.append(workflow.approve(current,x_actor_id,frozenset(x_roles.split(","))))
    except PermissionError as exc:raise HTTPException(403,"transition denied") from exc
def run():
    import uvicorn; uvicorn.run("taxflow_regulatory.api:app",host="0.0.0.0",port=8082)
