from pathlib import Path
from uuid import uuid4
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path[:0]=[str(ROOT/'services/query-service/src'),str(ROOT/'services/regulatory-service/src')]
from taxflow_query.shadow_tax_repository import InMemoryShadowTaxRepository
from taxflow_regulatory.repository import ChangeNotFound,InMemoryChangeRepository
def test_empty_tenant_scopes_never_fall_back_to_global():
    assert InMemoryShadowTaxRepository().history(uuid4(),'12345678000199')==()
    try:InMemoryChangeRepository().history(uuid4(),uuid4())
    except ChangeNotFound:pass
    else:raise AssertionError('existence disclosed')
