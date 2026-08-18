from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_local_observability_compose_has_healthchecked_core_services():
    compose = yaml.safe_load((ROOT / "deploy/observability/docker-compose.yml").read_text())
    services = compose["services"]
    assert {"otel-collector", "prometheus", "alertmanager", "grafana"} <= set(services)
    assert "healthcheck" in services["prometheus"]
    assert services["grafana"]["depends_on"]["prometheus"]["condition"] == "service_healthy"


def test_local_alerting_has_no_external_destination_or_secret():
    alertmanager = yaml.safe_load((ROOT / "deploy/observability/alertmanager.yml").read_text())
    assert alertmanager["receivers"][0]["webhook_configs"] == []
    text = (ROOT / "deploy/observability/docker-compose.yml").read_text().lower()
    assert "password" not in text and "token" not in text
