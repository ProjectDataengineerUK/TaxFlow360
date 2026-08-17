from hashlib import sha256
from pathlib import Path
import re

SECRET_PATTERNS=(re.compile(rb"(?i)(password|api[_-]?key|secret)\s*[:=]\s*[^\s,;]+"),re.compile(rb"(?i)authorization:\s*bearer\s+[^\s]+"))
def evidence_digest(path:Path)->str:
    digest=sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):digest.update(block)
    return digest.hexdigest()
def assert_redacted(path:Path)->None:
    data=path.read_bytes()
    if any(pattern.search(data) for pattern in SECRET_PATTERNS):raise ValueError("evidence contains possible secret")
def content_address(path:Path)->tuple[str,str]:
    assert_redacted(path); digest=evidence_digest(path); return f"evidence/sha256/{digest}",digest
