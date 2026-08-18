from pathlib import Path
import yaml


ROOT = Path(__file__).resolve().parents[2]


def test_managed_data_plane_contract_is_four_eyes_and_multi_cloud():
    document = yaml.safe_load((ROOT / "config/managed-data-plane-contract.yaml").read_text())
    assert document["status"] == "approved"
    assert document["approval"]["preparedBy"] != document["approval"]["approvedBy"]
    providers = document["services"]
    for service in ("relational", "event_backbone", "cache", "observability"):
        assert set(providers[service]["providers"]) == {"aws", "azure", "gcp"}


def test_managed_data_plane_security_invariants():
    document = yaml.safe_load((ROOT / "config/managed-data-plane-contract.yaml").read_text())
    security = document["security"]
    assert security["public_endpoints"] is False
    assert security["workload_identity_required"] is True
    assert security["static_credentials_forbidden"] is True
    assert document["services"]["cache"]["source_of_truth"] is False
    assert document["services"]["observability"]["logs"]["audit_retention_days"] >= 2555
