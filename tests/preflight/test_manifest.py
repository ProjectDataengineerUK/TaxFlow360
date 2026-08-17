from pathlib import Path
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/preflight/src"))
from taxflow_preflight.detect import load_manifest


def test_manifest_is_approved_and_four_eyes():
    raw, tools = load_manifest(ROOT / "config/local-toolchains.yaml")
    assert raw["status"] == "approved"
    assert raw["approval"]["preparedBy"] != raw["approval"]["approvedBy"]
    assert {tool.id for tool in tools} == {"java", "node", "terraform", "databricks", "gradle-wrapper"}


def test_manifest_is_exact_and_official():
    _, tools = load_manifest(ROOT / "config/local-toolchains.yaml")
    for tool in tools:
        assert len(tool.sha256) == 64
        assert "latest" not in tool.archive_url.lower()
        assert tool.version in unquote(tool.archive_url) or tool.id == "gradle-wrapper"
