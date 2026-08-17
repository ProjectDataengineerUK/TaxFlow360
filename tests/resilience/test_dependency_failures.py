from datetime import datetime,timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'services/regulatory-service/src'))
from taxflow_regulatory.copilot import RegulatoryCopilot
from taxflow_regulatory.search import InMemoryHybridSearch,SearchScope
class UnavailableModel:version='unavailable'
def test_empty_evidence_refuses_without_calling_model():
    answer=RegulatoryCopilot(InMemoryHybridSearch(),UnavailableModel()).answer('qual regra?',SearchScope(datetime.now(timezone.utc),('a',),('law',),'BR'))
    assert answer.disposition=='refused' and not answer.claims
