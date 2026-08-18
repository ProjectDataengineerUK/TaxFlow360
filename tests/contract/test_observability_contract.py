from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_observability_configuration_is_approved_and_four_eyes():
    slos = yaml.safe_load((ROOT / "config/observability-slos.yaml").read_text())
    alerts = yaml.safe_load((ROOT / "config/observability-alerts.yaml").read_text())
    assert slos["status"] == alerts["status"] == "approved"
    assert slos["governance"]["preparedBy"] != slos["governance"]["approvedBy"]
    assert len(slos["service_level_objectives"]) >= 6
    assert len(alerts["alerts"]) >= 6


def test_collector_redacts_sensitive_attributes_and_has_all_pipelines():
    collector = yaml.safe_load((ROOT / "config/otel-collector.yaml").read_text())
    actions = collector["processors"]["attributes/redact"]["actions"]
    deleted = {item["key"] for item in actions if item["action"] == "delete"}
    assert {"cpf", "cnpj", "authorization", "db.statement"} <= deleted
    assert set(collector["service"]["pipelines"]) == {"traces", "metrics", "logs"}


def test_dashboard_is_valid_json_and_has_operational_panels():
    dashboard = json.loads((ROOT / "dashboards/grafana/taxflow-overview.json").read_text())
    assert len(dashboard["panels"]) >= 5
    assert any(panel["title"] == "Critical divergences" for panel in dashboard["panels"])
