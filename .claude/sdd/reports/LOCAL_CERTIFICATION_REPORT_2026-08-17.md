# TaxFlow 360 — Certificação local

Data: 2026-08-17  
Candidato: commit `9434c10`  
Escopo: dados sintéticos, execução local, sem credenciais de nuvem

## Resultado

| Gate | Resultado | Evidência |
|---|---|---|
| Python regression | PASS | 84 testes, 2 warnings de dependência/cache |
| JVM tenant-service | PASS | Gradle/JUnit, BUILD SUCCESSFUL |
| JVM tax-service | PASS | Gradle/JUnit, BUILD SUCCESSFUL |
| JVM payment-service | PASS | Gradle/JUnit, código 0 |
| JVM reconciliation-service | PASS | 4 testes, após correção de fingerprint de idempotência |
| Frontend typecheck | PASS | `tsc --noEmit` |
| Frontend production build | PASS | Next.js 15.5.0, 9 rotas estáticas |
| Terraform formatting | PASS | `terraform fmt -check -recursive` |
| Terraform certification validate | PASS | `init -backend=false` + `validate` |
| Databricks workspace/streaming | BLOCKED | workspace, Unity Catalog, CDF e serverless não configurados |
| Databricks AI Search | BLOCKED | workspace e AI Search não configurados |
| Terraform AWS/Azure/GCP plan | BLOCKED | sem contas, providers autorizados ou credenciais |
| E2E hospedado | BLOCKED | ambiente protegido não provisionado |
| Integrated 100k hosted | BLOCKED | gate hospedado pendente |
| Tax catalog approval | BLOCKED | aprovação fiscal humana pendente |
| Regulatory corpus approval | BLOCKED | aprovação regulatória humana pendente |
| Security approval | BLOCKED | aprovação independente pendente |

## Decisão

`BLOCKED`: a certificação local está aprovada para desenvolvimento, mas não para `APPROVED_FOR_RC`. A política exige evidência de todos os gates obrigatórios e as aprovações four-eyes antes da promoção.

## Reprodutibilidade

- Toolchain: Temurin 21.0.5+11, Gradle 8.12.1, Node 22.14.0, Terraform 1.10.5, Databricks CLI 0.240.0.
- Artefatos executáveis foram obtidos de origens oficiais e verificados por SHA-256 no manifesto `config/local-toolchains.yaml`.
- Nenhum dado real, segredo, deploy, `plan` cloud ou acesso a workspace foi utilizado.

## Próxima ação autorizada

Provisionar um ambiente sandbox protegido com workload identities, orçamento aprovado, corpus tributário/regulatório aprovado e operadores responsáveis; então executar somente o workflow `certification-hosted` para o mesmo commit.
