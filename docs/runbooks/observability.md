# Observabilidade operacional

O Collector OpenTelemetry em `config/otel-collector.yaml` recebe OTLP por gRPC/HTTP, remove PII e credenciais, adiciona ambiente/namespace e exporta para o backend OTLP configurado por `OTEL_EXPORTER_OTLP_ENDPOINT`. O padrão local usa `localhost` e `debug`; não há endpoint ou segredo versionado.

## Execução local

```powershell
otelcol-contrib --config config/otel-collector.yaml
```

Serviços devem propagar W3C Trace Context e emitir `service.name`, `deployment.environment`, `tenant_hash` e `cloud`. Nunca emitir CPF, CNPJ, payload fiscal integral, Authorization ou SQL.

## SLOs e alertas

Os objetivos estão em `config/observability-slos.yaml`; regras Prometheus em `config/observability-alerts.yaml`; dashboard Grafana em `dashboards/grafana/taxflow-overview.json`. Alertas críticos exigem resposta e registro de incidente. Falta de evidência é `BLOCKED`, não sucesso silencioso.

Origens: [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/), [OTLP](https://opentelemetry.io/docs/specs/otlp/), [Prometheus alerting](https://prometheus.io/docs/alerting/latest/overview/) e [Grafana dashboards](https://grafana.com/docs/grafana/latest/dashboards/).
