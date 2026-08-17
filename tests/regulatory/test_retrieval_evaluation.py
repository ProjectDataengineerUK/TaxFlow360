from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'services/regulatory-service/src')); sys.path.insert(0,str(ROOT/'data/databricks/src'))
from taxflow_regulatory.models import Chunk
from taxflow_regulatory.search import InMemoryHybridSearch,SearchScope
from regulatory_evaluation import evaluate
def test_temporal_authority_and_tenant_filters():
    base=dict(document_version_id='v',document_type='constitution',jurisdiction='BR',canonical_url='https://www.planalto.gov.br/ccivil_03/x',document_id='d',locator='art',text='IBS artigo',content_sha256='a'*64,valid_from=datetime(2023,1,1,tzinfo=timezone.utc))
    public=Chunk(chunk_id='public',authority_id='planalto',**base); private=Chunk(chunk_id='private',authority_id='planalto',tenant_id=uuid4(),**base)
    scope=SearchScope(datetime(2026,1,1,tzinfo=timezone.utc),('planalto',),('constitution',),'BR','other')
    assert [x.chunk_id for x in InMemoryHybridSearch((public,private)).hybrid_search('IBS',scope)]==['public']
def test_quality_gate():assert evaluate({'q':{'c'}},{'q':['c']},1,1,3,3).passed
