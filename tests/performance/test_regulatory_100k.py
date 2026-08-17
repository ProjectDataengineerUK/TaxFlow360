from datetime import datetime,timezone
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'services/regulatory-service/src'))
from taxflow_regulatory.models import Chunk
from taxflow_regulatory.search import InMemoryHybridSearch,SearchScope
def test_100k_chunks_are_accounted_and_searchable():
    base=dict(document_version_id='v',authority_id='a',document_type='law',jurisdiction='BR',canonical_url='https://www.planalto.gov.br/ccivil_03/x',document_id='d',locator='art',content_sha256='a'*64)
    chunks=tuple(Chunk(chunk_id=str(i),text=('target IBS' if i==99999 else 'other'),**base) for i in range(100_000)); assert len(chunks)==100_000
    start=time.perf_counter(); found=InMemoryHybridSearch(chunks).hybrid_search('target IBS',SearchScope(datetime.now(timezone.utc),('a',),('law',),'BR'))
    assert found[0].chunk_id=='99999' and time.perf_counter()-start<2
