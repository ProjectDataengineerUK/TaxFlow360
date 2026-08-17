from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Literal

Status = Literal["PASS", "FAIL", "BLOCKED"]


@dataclass(frozen=True)
class ToolSpec:
    id: str
    version: str
    official_hosts: tuple[str, ...]
    archive_url: str
    sha256: str
    max_archive_bytes: int
    archive_root: str
    executable: str
    version_args: tuple[str, ...]
    version_pattern: str
    repository_target: str | None = None

    @property
    def cache_key(self) -> str:
        return f"{self.id}/{self.version}/{self.sha256}"


@dataclass(frozen=True)
class Observation:
    tool: str
    status: Status
    expected_version: str
    executable: str | None
    observed_version: str | None
    artifact_sha256: str | None
    reason: str


def cache_root(value: str | None) -> Path:
    if value:
        path = Path(value).expanduser().resolve()
    elif os.name == "nt" and os.getenv("LOCALAPPDATA"):
        path = (Path(os.environ["LOCALAPPDATA"]) / "TaxFlow360" / "tool-cache").resolve()
    else:
        path = (Path.home() / ".taxflow360" / "tool-cache").resolve()
    return path
