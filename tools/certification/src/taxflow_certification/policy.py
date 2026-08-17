from hashlib import sha256
import json
from .models import Approval,Candidate,Decision,GateResult,GateStatus
from .registry import Registry

def complete_matrix(candidate:Candidate,registry:Registry,recorded:tuple[GateResult,...])->tuple[GateResult,...]:
    latest={}
    for result in recorded:
        if result.run_id!=candidate.run_id:continue
        previous=latest.get(result.gate_id)
        if previous is None or result.attempt>previous.attempt:latest[result.gate_id]=result
    return tuple(latest.get(gate.id,GateResult.blocked(candidate.run_id,gate.id,"no evidence recorded")) for gate in registry.gates)
def evaluate_release(candidate:Candidate,registry:Registry,results:tuple[GateResult,...],approvals:tuple[Approval,...])->Decision:
    matrix=complete_matrix(candidate,registry,results); definitions={g.id:g for g in registry.gates}
    blockers=[r.gate_id for r in matrix if definitions[r.gate_id].required and r.status!=GateStatus.PASS]
    approved={a.gate_id:a for a in approvals if a.decision=="approved"}
    for gate_id in registry.human_approvals:
        if gate_id not in approved: blockers.append(gate_id+":approval-missing")
    actors=[approved[g].actor_id for g in registry.human_approvals if g in approved]
    if len(actors)!=len(set(actors)):blockers.append("independent-human-approvals-required")
    payload=[r.model_dump(mode="json") for r in matrix]
    matrix_hash=sha256(json.dumps(payload,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
    return Decision(status="BLOCKED" if blockers else "APPROVED_FOR_RC",blockers=tuple(sorted(set(blockers))),candidate_sha=candidate.candidate_sha,matrix_sha256=matrix_hash)
