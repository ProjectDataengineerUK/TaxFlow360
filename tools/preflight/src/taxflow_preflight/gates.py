from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

ALLOWED_TERRAFORM = {"version", "fmt", "validate", "test"}
FORBIDDEN = {"apply", "destroy", "import", "plan", "refresh"}


def validate_terraform_args(args: tuple[str, ...]) -> None:
    if not args or args[0] not in ALLOWED_TERRAFORM or any(a.lower() in FORBIDDEN for a in args):
        raise PermissionError("Terraform command is outside local enablement scope")
    if any("credential" in a.lower() or "profile" in a.lower() for a in args):
        raise PermissionError("credential/profile arguments are prohibited")


@dataclass(frozen=True)
class GateResult:
    name: str
    status: str
    return_code: int | None
    output: str


def run_command(name: str, argv: tuple[str, ...], cwd: Path, timeout: int = 600) -> GateResult:
    if not argv:
        return GateResult(name, "BLOCKED", None, "empty command")
    if Path(argv[0]).name.lower().startswith("terraform"):
        validate_terraform_args(argv[1:])
    try:
        result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                                timeout=timeout, check=False, shell=False)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return GateResult(name, "BLOCKED", None, str(exc))
    output = (result.stdout + result.stderr)[-20000:]
    return GateResult(name, "PASS" if result.returncode == 0 else "FAIL", result.returncode, output)
