from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

import yaml

from .models import Observation, ToolSpec

SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load_manifest(path: Path) -> tuple[dict, tuple[ToolSpec, ...]]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw.get("status") != "approved":
        raise ValueError("toolchain manifest is not approved")
    approval = raw.get("approval", {})
    if not approval.get("preparedBy") or approval.get("preparedBy") == approval.get("approvedBy"):
        raise ValueError("manifest requires distinct four-eyes actors")
    tools = []
    for item in raw.get("tools", []):
        url = item["archiveUrl"]
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in item["officialHosts"]:
            raise ValueError(f"unapproved origin for {item['id']}")
        if not SHA256.fullmatch(item["sha256"]):
            raise ValueError(f"invalid sha256 for {item['id']}")
        tools.append(ToolSpec(
            id=item["id"], version=str(item["version"]),
            official_hosts=tuple(item["officialHosts"]), archive_url=url,
            sha256=item["sha256"], max_archive_bytes=int(item["maxArchiveBytes"]),
            archive_root=item.get("archiveRoot", ""), executable=item["executable"],
            version_args=tuple(item.get("versionArgs", [])),
            version_pattern=item["versionPattern"], repository_target=item.get("repositoryTarget"),
        ))
    if not tools:
        raise ValueError("manifest contains no tools")
    return raw, tuple(tools)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_executable(spec: ToolSpec, root: Path, repository: Path) -> Path:
    if spec.repository_target:
        return (repository / spec.repository_target).resolve()
    base = root / spec.id / spec.version / spec.sha256
    return (base / spec.archive_root / spec.executable).resolve()


def detect(spec: ToolSpec, root: Path, repository: Path) -> Observation:
    executable = expected_executable(spec, root, repository)
    if not executable.is_file():
        return Observation(spec.id, "BLOCKED", spec.version, None, None, None, "verified artifact is absent")
    artifact_hash = sha256(executable) if spec.repository_target else None
    if spec.repository_target:
        status = "PASS" if artifact_hash == spec.sha256 else "FAIL"
        return Observation(spec.id, status, spec.version, str(executable), None, artifact_hash,
                           "checksum verified" if status == "PASS" else "checksum mismatch")
    try:
        completed = subprocess.run([str(executable), *spec.version_args], capture_output=True,
                                   text=True, timeout=15, check=False, shell=False)
    except OSError as exc:
        return Observation(spec.id, "FAIL", spec.version, str(executable), None, None, str(exc))
    output = (completed.stdout + completed.stderr).strip()
    passed = completed.returncode == 0 and re.search(spec.version_pattern, output, re.MULTILINE)
    return Observation(spec.id, "PASS" if passed else "FAIL", spec.version, str(executable), output, None,
                       "expected version observed" if passed else "unexpected version or exit status")
