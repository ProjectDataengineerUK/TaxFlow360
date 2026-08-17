# TaxFlow 360 — módulos previstos e estado de implementação

> Inventário consolidado em 2026-08-17 a partir de `context.md`, código, Designs SDD e Build Reports.

## Legenda

| Estado | Significado |
|--------|-------------|
| Implementado localmente | Código, contrato e testes locais existem; pode depender de gate hospedado |
| Parcial | Parte relevante existe, mas faltam capacidades descritas no `context.md` |
| Não iniciado | Não há módulo funcional específico; pode haver apenas previsão arquitetural |

Nenhum item deste documento significa produção homologada. Dados, regras e corpus continuam sintéticos até aprovação especializada e execução dos gates hospedados.

## Núcleo previsto no context.md

| # | Módulo previsto | Estado | Entrega existente | Principal lacuna |
|---|-----------------|--------|------------------|------------------|
| 1 | Entrada de dados | Implementado localmente | `ingestion-service`, modelos canônicos, CSV/XML/XLSX plugáveis, quarentena, idempotência e gerador sintético | APIs/SFTP/webhooks e integrações proprietárias reais |
| 2 | Tax Readiness Score | Implementado localmente | Metodologia com 8 dimensões, score, evidências, histórico, comparação, Gold e UI | Execução Databricks hospedada e dados empresariais reais |
| 3 | Simulação do modelo atual | Implementado localmente | Tax Simulation atual com Decimal, memória, regras, fontes e casos dourados | Catálogo tributário real aprovado |
| 4 | Cenário tributário futuro CBS/IBS | Implementado localmente | Cenários reform/split, componentes CBS/IBS, comparação e fontes oficiais | Alíquotas/vigências produtivas homologadas |
| 5 | Real-Time Tax Engine | Parcial | Motor Kotlin, API, idempotência e pipeline analítico | Kafka/MSK e benchmarks transacionais hospedados em milissegundos |
| 6 | Tax Rule Engine | Implementado localmente | Regra imutável/versionada, vigência, four-eyes, memória e provenance | Catálogo completo por NCM/NBS/regime/localidade e aprovação fiscal real |
| 7 | Simulador de Split Payment | Implementado localmente | Payment Engine, parcelas, split, conservação, estorno/devolução e simulações | Protocolos reais de bancos/PSPs/Fisco |
| 8 | Simulação por meio de pagamento | Parcial | Estrutura para métodos, parcelas, reversal/refund e política de tolerância | Matriz completa Pix/cartão/boleto/TED/TEF/voucher/antecipação |
| 9 | Bank Readiness / Payment Tax Gateway | Parcial | `payment-service`, reconciliação, split e contratos | Score bancário, 1 milhão de transações e integrações certificadas com instituições |
| 10 | Simulador para bancos | Não iniciado | Casos genéricos de pagamento servem como base | Produto dedicado, cenários bancários e Bank Readiness Score |
| 11 | Fisco Simulator / Fiscal Mirror | Parcial | Shadow Tax reconstrói e compara fiscal/ERP/pagamento/split | Visão dedicada de apuração, créditos/débitos e perspectiva completa do Fisco |
| 12 | Conciliação de quatro pontas | Implementado localmente | Documento/ERP/pagamento/split, tolerância, severidade, replay e revisão humana | Validação streaming hospedada e integrações reais |
| 13 | Tax Transaction ID | Implementado localmente | Identidade canônica usada em ingestão, cálculo, projeção e conciliação | Adoção por integrações externas reais |
| 14 | Capital de Giro Digital Twin | Implementado localmente | Ledger diário, baseline, caixa, gap, float tributário e 9 cenários | Calibração com dados reais e runtime Databricks/MLflow |
| 15 | IA de capital de giro | Parcial | Adapter MLflow, backtest/gates e fallback determinístico | Modelo promovido e recomendações operacionais governadas |
| 16 | Cash Stress Test | Implementado localmente | 6 stresses independentes e 3 combinados, horizontes 30/90/180/365 | Calibração e validação financeira real |
| 17 | Tax Migration Journey | Parcial | Readiness, simulação, Shadow, reconciliação e certificação existem como fases | Workflow único de projeto, tarefas, responsáveis e etapas 1–10 |
| 18 | Shadow Tax | Implementado localmente | Event ledger, watermark, dedup, four-way match, divergências, métricas e fila humana | Workspace streaming e p95 hospedado |
| 19 | Migration Command Center | Parcial | Control Tower com páginas Readiness, Simulator, Digital Twin, Shadow e Regulatory | Dashboard consolidado vivo, alertas e workflow de migração |
| 20 | Copilot Tributário | Implementado localmente | Retrieval filtrado, claims tipadas, citações determinísticas e recusa sem fonte | Model gateway empresarial e avaliação com corpus fiscal real |
| 21 | Regulatory AI | Implementado localmente | Allowlist oficial, snapshots bitemporais, chunking, diff, Change Request e four-eyes | Captura real aprovada, Databricks AI Search e revisão especializada |
| 22 | Timeline regulatória | Parcial | Metadados temporais, versões, diff e UI regulatória básica | Timeline empresarial completa e alertas por tributo/jurisdição |
| 23 | Simulador temporal 2026–2033 | Parcial | Vigência/cutoff e horizontes financeiros | Seletor anual completo com faturamento, impostos, EBITDA, margem e financiamento |
| 24 | Supplier Readiness | Não iniciado | Previsto como consumidor futuro dos produtos de dados | Score, contrato, motor, API e UI próprios |
| 25 | Customer Readiness | Não iniciado | Previsto no roadmap de ecossistema | Score, contrato, motor, API e UI próprios |
| 26 | Pricing Simulator / Smart Pricing | Não iniciado | Digital Twin oferece bases financeiras | Motor de preço/margem/crédito/cash conversion e UI |
| 27 | Tax Profitability | Não iniciado | Gold financeiro/fiscal pode alimentar o módulo | Rentabilidade por produto/cliente/canal/região e semantic model |
| 28 | Tax Control Tower | Parcial | Next.js com páginas dos principais módulos | Autenticação/SSO real, dados hospedados, alertas e visão executiva consolidada |

## Plataforma e arquitetura previstas

| Capacidade | Estado | Implementado | Pendente |
|------------|--------|-------------|----------|
| SaaS multi-tenant | Implementado localmente | Tenant service, RBAC, headers, repositories tenant-scoped e PostgreSQL forced RLS | IdP/SSO e testes hospedados completos |
| Java/Kotlin transacional | Implementado localmente | Tenant, Tax, Payment e Reconciliation services | Compilação/JUnit hospedados; Java/Gradle indisponíveis localmente |
| Python/Data/IA | Implementado localmente | Ingestion, Query, Regulatory, referências e workloads Databricks | Ambientes/serving hospedados |
| Next.js/React/TypeScript | Implementado localmente | Control Tower e páginas funcionais estáticas/tenant-aware | `npm ci`, typecheck/build e E2E hospedados |
| Kafka/MSK/event streaming | Parcial | Contratos, outbox, CDF e semântica idempotente | Broker real, schemas registrados e operação hosted |
| PostgreSQL/Aurora | Parcial | Migrations, RLS, append-only e outbox | Aurora staging/prod, backup/restore e observabilidade |
| Redis/cache | Não iniciado | Previsto na arquitetura | Adapter, tenancy, invalidação e testes de vazamento |
| S3/ADLS/GCS | Implementado em IaC | Storage criptografado/versionado para três clouds | Plans/applies com contas sandbox |
| Databricks/Delta/Unity Catalog | Implementado como código | Bundles, Bronze/Silver/Gold, CDF, MLflow adapter e AI Search spec | Workspace real e gates de execução |
| AWS/Azure/GCP | Implementado em IaC | Contrato Terraform comum e adapters | `terraform validate/test/plan` com providers/credenciais |
| EKS/ECS/Kubernetes | Não iniciado | Apenas previsto no `context.md`/arquitetura | Manifests/módulos, imagens e runtime |
| Observabilidade | Parcial | Campos de logging/tracing, métricas e desenhos OpenTelemetry | Collector/backends, dashboards e alertas operacionais reais |
| Power BI | Não iniciado | Nenhum artefato específico | Semantic model, datasets e dashboards |
| Cognito/SSO/Secrets Manager | Não iniciado | Interfaces e regras de workload identity/sem segredo | Recursos e integração reais por cloud |
| CI/CD e certificação | Implementado localmente | Workflows, 17 gates, evidence ledger, SBOM/attestation design e matriz BLOCKED | Execução hosted, registry/signing e aprovações humanas |

## Produtos e edições comerciais

| Produto previsto | Estado |
|------------------|--------|
| TaxFlow Enterprise | Arquitetura prevista; empacotamento/isolamento dedicado não implementado |
| TaxFlow ERP | APIs e contratos base existem; produto/SDK para ERPs não implementado |
| TaxFlow Bank | Payment/Reconciliation parciais; edição bancária não implementada |
| TaxFlow Accounting | Multi-CNPJ previsto; experiência específica não implementada |
| TaxFlow Advisory | Fluxos de análise/revisão existem; edição comercial não implementada |
| TaxFlow API | OpenAPI e serviços existem; gateway, quotas, billing e portal não implementados |
| TaxFlow Sovereign/Financial | Arquitetura prevista; deployment isolado/certificado não implementado |

## Capacidades comerciais e longo prazo

Ainda não implementados: planos e billing SaaS, cobrança por CNPJ/transação, marketplace, portal de parceiros, estratégia de entrada comercial no produto, Tax Transaction Network, operação produtiva de split, certificações externas e onboarding de clientes reais.

## Resumo executivo

| Classificação | Quantidade entre os 28 módulos funcionais |
|---------------|-------------------------------------------|
| Implementado localmente | 13 |
| Parcial | 10 |
| Não iniciado | 5 |

O núcleo solicitado inicialmente — Readiness, Simulador, Digital Twin e Shadow Tax — está implementado localmente. Regulatory AI/Copilot e a estrutura de certificação também foram adicionados. A finalização agora depende principalmente de runtimes hospedados, conteúdo tributário aprovado e dos módulos complementares ainda fora do núcleo.
