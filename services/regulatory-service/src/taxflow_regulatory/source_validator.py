from dataclasses import dataclass
from hashlib import sha256
from ipaddress import ip_address
from urllib.parse import urlsplit
import socket

@dataclass(frozen=True)
class ApprovedSource:
    source_id:str; host:str; path_prefixes:tuple[str,...]

class SourceValidationError(ValueError): pass

def validate_url(url:str,sources:tuple[ApprovedSource,...],*,resolve_dns:bool=False)->ApprovedSource:
    parsed=urlsplit(url)
    if parsed.scheme!="https" or parsed.username or parsed.password or parsed.fragment or parsed.query:
        raise SourceValidationError("canonical source URL must be credential-free HTTPS without query or fragment")
    host=(parsed.hostname or "").rstrip(".").lower()
    source=next((s for s in sources if host==s.host and any(parsed.path.startswith(p) for p in s.path_prefixes)),None)
    if source is None: raise SourceValidationError("source is not allowlisted")
    if resolve_dns:
        for result in socket.getaddrinfo(host,443,type=socket.SOCK_STREAM):
            address=ip_address(result[4][0]);
            if not address.is_global: raise SourceValidationError("private or reserved target denied")
    return source

def verify_content(content:bytes,expected_sha256:str,max_bytes:int=10_485_760)->str:
    if len(content)>max_bytes: raise SourceValidationError("document exceeds size limit")
    actual=sha256(content).hexdigest()
    if actual!=expected_sha256: raise SourceValidationError("content hash mismatch")
    return actual
