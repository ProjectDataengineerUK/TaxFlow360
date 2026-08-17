from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from .models import Chunk

@dataclass(frozen=True)
class SearchScope:
    cutoff_at:datetime; authority_ids:tuple[str,...]; document_types:tuple[str,...]; jurisdiction:str; tenant_id:str|None=None

def validate_scope(scope:SearchScope)->None:
    if not scope.authority_ids or not scope.document_types or not scope.jurisdiction: raise ValueError("mandatory retrieval filters missing")

class SearchPort(Protocol):
    def hybrid_search(self,query:str,scope:SearchScope,limit:int=10)->tuple[Chunk,...]: ...

class InMemoryHybridSearch:
    def __init__(self,chunks:tuple[Chunk,...]=()): self.chunks=chunks
    def hybrid_search(self,query:str,scope:SearchScope,limit:int=10)->tuple[Chunk,...]:
        validate_scope(scope); terms=set(query.lower().split()); ranked=[]
        for chunk in self.chunks:
            if chunk.authority_id not in scope.authority_ids or chunk.document_type not in scope.document_types or chunk.jurisdiction!=scope.jurisdiction: continue
            if chunk.tenant_id is not None and str(chunk.tenant_id)!=scope.tenant_id: continue
            if chunk.valid_from and chunk.valid_from>scope.cutoff_at or chunk.valid_to and chunk.valid_to<=scope.cutoff_at: continue
            score=len(terms & set(chunk.text.lower().split()))/max(len(terms),1)
            if score: ranked.append(chunk.model_copy(update={"score":score}))
        return tuple(sorted(ranked,key=lambda x:(-x.score,x.chunk_id))[:limit])
