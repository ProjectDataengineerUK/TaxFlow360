import argparse,json
from datetime import datetime
from pathlib import Path
from .models import Approval,Candidate,GateResult
from .policy import evaluate_release
from .registry import load_registry

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--registry",default="config/certification-gates.yaml"); sub=parser.add_subparsers(dest="command",required=True)
    init=sub.add_parser("init"); init.add_argument("--rc",required=True); init.add_argument("--sha",required=True); init.add_argument("--cutoff",required=True); init.add_argument("--out",required=True)
    check=sub.add_parser("evaluate"); check.add_argument("--candidate",required=True); check.add_argument("--results",required=True); check.add_argument("--approvals",required=True)
    args=parser.parse_args(); registry=load_registry(args.registry)
    if args.command=="init":
        candidate=Candidate(release_candidate=args.rc,candidate_sha=args.sha,registry_checksum=registry.checksum,tool_versions={},logical_cutoff=datetime.fromisoformat(args.cutoff.replace("Z","+00:00")))
        Path(args.out).write_text(candidate.model_dump_json(indent=2),encoding="utf-8"); return
    candidate=Candidate.model_validate_json(Path(args.candidate).read_text()); results=tuple(GateResult.model_validate(x) for x in json.loads(Path(args.results).read_text())); approvals=tuple(Approval.model_validate(x) for x in json.loads(Path(args.approvals).read_text()))
    if candidate.registry_checksum!=registry.checksum: raise SystemExit("candidate registry checksum mismatch")
    decision=evaluate_release(candidate,registry,results,approvals); print(decision.model_dump_json(indent=2)); raise SystemExit(0 if decision.status=="APPROVED_FOR_RC" else 1)
if __name__=="__main__":main()
