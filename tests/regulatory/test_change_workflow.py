from pathlib import Path
from uuid import uuid4
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'services/regulatory-service/src'))
from taxflow_regulatory.change_workflow import ChangeWorkflow
from taxflow_regulatory.models import ChangeRequest
def draft():return ChangeRequest(change_request_id=uuid4(),tenant_id=uuid4(),version=1,status='DRAFT',source_document_version_ids=('v',),affected_rule_ids=('r',),diff_sha256='a'*64,created_by='author')
def test_four_eyes_and_no_ai_publish():
    flow=ChangeWorkflow(); submitted=flow.submit(draft(),'author',frozenset({'REGULATORY_AUTHOR'}),'reviewed'); tested=submitted.model_copy(update={'golden_tests_passed':True})
    try:flow.approve(tested,'author',frozenset({'REGULATORY_APPROVER'}))
    except PermissionError:pass
    else:raise AssertionError('self approval')
    assert flow.approve(tested,'reviewer',frozenset({'REGULATORY_APPROVER'})).status=='APPROVED'
    try:flow.publish(tested)
    except PermissionError:pass
    else:raise AssertionError('AI published rule')
