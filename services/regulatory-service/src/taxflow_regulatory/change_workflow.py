from dataclasses import replace
from .models import ChangeRequest

class ChangeWorkflow:
    def submit(self,change:ChangeRequest,actor_id:str,roles:frozenset[str],justification:str)->ChangeRequest:
        if change.status!="DRAFT" or "REGULATORY_AUTHOR" not in roles or not justification.strip(): raise PermissionError("submission denied")
        return change.model_copy(update={"version":change.version+1,"status":"SUBMITTED","submitted_by":actor_id,"justification":justification})
    def approve(self,change:ChangeRequest,actor_id:str,roles:frozenset[str])->ChangeRequest:
        if "REGULATORY_APPROVER" not in roles or change.status!="SUBMITTED": raise PermissionError("approval denied")
        if actor_id in {change.created_by,change.submitted_by} or not change.golden_tests_passed: raise PermissionError("four-eyes and passing golden tests required")
        return change.model_copy(update={"version":change.version+1,"status":"APPROVED","approved_by":actor_id})
    def publish(self,*_args,**_kwargs): raise PermissionError("Regulatory AI cannot publish productive rules")
