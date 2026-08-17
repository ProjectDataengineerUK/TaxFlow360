from datetime import datetime
from typing import Protocol
from .citations import UnsupportedClaim,validate_claims
from .guardrails import UnsafeContent,build_context,inspect_text
from .models import Claim,CopilotAnswer
from .search import SearchPort,SearchScope

class ModelPort(Protocol):
    version:str
    def claims(self,question:str,context:str)->tuple[Claim,...]: ...

class RegulatoryCopilot:
    def __init__(self,search:SearchPort,model:ModelPort,policy_version:str="1.0.0"): self.search=search; self.model=model; self.policy_version=policy_version
    def answer(self,question:str,scope:SearchScope)->CopilotAnswer:
        inspect_text(question); chunks=self.search.hybrid_search(question,scope)
        if not chunks: return self._refuse(scope.cutoff_at,"official evidence not found")
        try:
            claims=self.model.claims(question,build_context(chunks)); citations=validate_claims(claims,chunks)
        except (UnsafeContent,UnsupportedClaim,ValueError): return self._refuse(scope.cutoff_at,"evidence or output validation failed")
        if not claims: return self._refuse(scope.cutoff_at,"model produced no supported claims")
        return CopilotAnswer(disposition="answered",claims=claims,citations=citations,cutoff_at=scope.cutoff_at,policy_version=self.policy_version,model_version=self.model.version)
    def _refuse(self,cutoff:datetime,reason:str)->CopilotAnswer:
        return CopilotAnswer(disposition="refused",reason=reason,cutoff_at=cutoff,policy_version=self.policy_version,model_version=self.model.version)
