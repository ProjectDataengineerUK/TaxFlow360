from datetime import datetime,timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'tools/certification/src'))
from taxflow_certification.models import Approval,Candidate,GateResult,GateStatus
from taxflow_certification.policy import evaluate_release
from taxflow_certification.registry import load_registry,validate_environment

def candidate(registry):return Candidate(release_candidate='0.1.0-rc.1',candidate_sha='a'*40,registry_checksum=registry.checksum,tool_versions={'python':'3.12.8'},logical_cutoff=datetime.now(timezone.utc))
def test_missing_evidence_is_blocked():
    registry=load_registry(ROOT/'config/certification-gates.yaml'); validate_environment(ROOT/'config/certification-environments.yaml')
    decision=evaluate_release(candidate(registry),registry,(),()); assert decision.status=='BLOCKED'; assert len(decision.blockers)>=len(registry.gates)
def test_all_required_gates_and_independent_humans_can_approve_rc():
    registry=load_registry(ROOT/'config/certification-gates.yaml'); c=candidate(registry); now=datetime.now(timezone.utc)
    results=tuple(GateResult(run_id=c.run_id,gate_id=g.id,attempt=1,status=GateStatus.PASS,environment='test',evidence_uri=f'evidence/{g.id}',evidence_sha256='b'*64,started_at=now,completed_at=now) for g in registry.gates)
    approvals=tuple(Approval(gate_id=gate,actor_id=f'actor-{i}',role='APPROVER',decision='approved',justification='verified') for i,gate in enumerate(registry.human_approvals))
    assert evaluate_release(c,registry,results,approvals).status=='APPROVED_FOR_RC'
