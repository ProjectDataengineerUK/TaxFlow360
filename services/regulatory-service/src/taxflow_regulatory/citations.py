from .models import Chunk,Claim,Citation

class UnsupportedClaim(ValueError): pass

def validate_claims(claims:tuple[Claim,...],retrieved:tuple[Chunk,...])->tuple[Citation,...]:
    chunks={chunk.chunk_id:chunk for chunk in retrieved}; cited=[]
    for claim in claims:
        if not claim.citation_chunk_ids or any(cid not in chunks for cid in claim.citation_chunk_ids):
            raise UnsupportedClaim("claim has unsupported citation")
        for cid in claim.citation_chunk_ids:
            chunk=chunks[cid]
            cited.append(Citation(chunk_id=cid,document_id=chunk.document_id,document_version_id=chunk.document_version_id,
                authority_id=chunk.authority_id,locator=chunk.locator,canonical_url=chunk.canonical_url,content_sha256=chunk.content_sha256))
    unique:dict[str,Citation]={}
    for item in cited: unique.setdefault(item.chunk_id,item)
    return tuple(unique.values())
