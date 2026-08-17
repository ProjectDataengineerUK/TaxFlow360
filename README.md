# TaxFlow 360

Plataforma multi-tenant para diagnóstico de prontidão tributária, simulação CBS/IBS e split payment, Digital Twin financeiro e Shadow Tax.

## Arquitetura

- Serviços transacionais independentes em Kotlin.
- Ingestão e consulta em Python.
- Eventos versionados com Avro e contratos ODCS.
- Lakehouse Databricks com camadas Bronze, Silver e Gold.
- Interface Next.js e infraestrutura Terraform para AWS, Azure e GCP.

Consulte [system-context.md](docs/architecture/system-context.md) e os artefatos SDD em `.claude/sdd/features/`.

## Desenvolvimento local

```powershell
python -m compileall services data tests
python -m unittest discover -s tests -p "test_*.py"
```

Os serviços mantêm ambientes e builds próprios. Credenciais devem vir de identidade de workload ou secret manager; nunca de arquivos versionados.

## Princípios

- Cálculo tributário determinístico, temporal e auditável.
- Isolamento de tenant em todas as camadas.
- Idempotência para qualquer efeito financeiro ou tributário.
- Databricks fora do caminho transacional crítico.
- Alterações regulatórias exigem revisão humana.

