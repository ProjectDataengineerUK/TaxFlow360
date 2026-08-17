from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/'services/regulatory-service/src'))
from taxflow_regulatory.models import Chunk,Claim
from taxflow_regulatory.source_validator import ApprovedSource,SourceValidationError,validate_url,verify_content
from taxflow_regulatory.citations import UnsupportedClaim,validate_claims

def test_official_allowlist_and_hash():
    source=ApprovedSource('planalto','www.planalto.gov.br',('/ccivil_03/',))
    assert validate_url('https://www.planalto.gov.br/ccivil_03/lei.htm',(source,)).source_id=='planalto'
    for bad in ('http://www.planalto.gov.br/ccivil_03/x','https://evil.invalid/ccivil_03/x','https://user:pass@www.planalto.gov.br/ccivil_03/x','https://www.planalto.gov.br/ccivil_03/x?q=1'):
        try:validate_url(bad,(source,))
        except SourceValidationError:pass
        else:raise AssertionError(bad)
    import hashlib; data=b'official snapshot'; assert verify_content(data,hashlib.sha256(data).hexdigest())
def test_claim_citation_must_be_retrieved():
    chunk=Chunk(chunk_id='c',document_version_id='v',authority_id='a',document_type='law',jurisdiction='BR',canonical_url='https://www.planalto.gov.br/ccivil_03/x',document_id='d',locator='art. 1',text='supported',content_sha256='a'*64)
    assert validate_claims((Claim(text='claim',citation_chunk_ids=('c',)),),(chunk,))[0].chunk_id=='c'
    try:validate_claims((Claim(text='claim',citation_chunk_ids=('invented',)),),(chunk,))
    except UnsupportedClaim:pass
    else:raise AssertionError('invented citation accepted')
