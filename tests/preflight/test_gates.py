from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/preflight/src"))
from taxflow_preflight.gates import validate_terraform_args


@pytest.mark.parametrize("args", [("version",), ("fmt", "-check"), ("validate",), ("test",)])
def test_safe_terraform_commands(args):
    validate_terraform_args(args)


@pytest.mark.parametrize("args", [("apply",), ("destroy",), ("plan",), ("validate", "-profile=prod")])
def test_unsafe_terraform_commands_are_rejected(args):
    with pytest.raises(PermissionError):
        validate_terraform_args(args)
