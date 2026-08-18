# TaxFlow 360

> Plataforma SaaS de inteligência tributária e financeira para preparar empresas para a transição da reforma tributária brasileira, conectando sistemas empresariais, motores tributários, meios de pagamento, split payment, conciliação fiscal e projeções de fluxo de caixa por meio de um digital twin tributário.

---

## Stack

- **Estado atual:** certificação local executada com Python/JVM/frontend/Terraform; certificação hospedada e produção permanecem bloqueadas
- **Cloud:** SaaS principal em AWS, com adapters Terraform para Azure e GCP
- **Backend proposto:** Java/Kotlin para o núcleo transacional e Python para dados e IA
- **Frontend proposto:** Next.js, React e TypeScript
- **Eventos:** Kafka / Amazon MSK
- **Dados:** Aurora PostgreSQL, Redis, S3, Databricks e Delta Lake
- **Analytics e IA:** Databricks SQL, MLflow, LLMs, forecasting e detecção de anomalias
- **Plataforma:** EKS, ECS, Terraform e GitHub Actions
- **Observabilidade:** CloudWatch e OpenTelemetry
- **BI:** Power BI
- **Identidade e segredos:** Cognito, SSO empresarial e AWS Secrets Manager

## Estrutura

```text
TaxFlow360/
├── .claude/       # Agentes, comandos, skills, KB e hooks do AgentCode
├── .codex/        # Configuração do AgentCode para Codex
├── .cursor/       # Regras, agentes e hooks para Cursor
├── apps/           # Control Tower Next.js
├── config/         # Metodologias, regras, fontes e políticas versionadas
├── contracts/      # OpenAPI, eventos e data contracts
├── data/databricks/# Bundles e pipelines Bronze/Silver/Gold/IA
├── deploy/terraform/# Contrato multi-cloud AWS/Azure/GCP
├── docs/           # Inventário e runbooks
├── services/       # Kotlin e Python services
├── tests/          # Golden, segurança, E2E, performance e conformance
├── tools/          # Orquestrador de certificação
├── CLAUDE.md       # Contexto operacional do projeto
└── context.md      # Visão de produto e proposta de arquitetura
```

## Arquivos-chave

| Arquivo | Função |
|---------|--------|
| `context.md` | Fonte atual da visão do produto, módulos, arquitetura, stack e estratégia comercial |
| `CLAUDE.md` | Contexto resumido para orientar agentes durante o desenvolvimento |
| `docs/MODULES_STATUS.md` | Inventário entre módulos previstos, implementados, parciais e pendentes |
| `.claude/sdd/features/DESIGN_PLATAFORMA_TAXFLOW_360.md` | Roadmap e arquitetura mestre SDD |
| `.claude/sdd/reports/` | Evidências e limitações de cada Build |
| `.claude/settings.json` | Configuração local dos hooks do AgentCode |

## Convenções

- **Contratos:** spec-linter SDD, OpenAPI, Avro e ODCS/YAML
- **Testes:** pytest local; JUnit/Next/Terraform/Databricks definidos para CI hospedada
- **Certificação:** 17 gates; evidência ausente deve resultar em `BLOCKED`
- O motor tributário deve permanecer independente da cloud.
- Regras tributárias precisam ser versionadas por vigência e manter memória de cálculo e fundamento legal.
- Alterações regulatórias devem passar por validação humana antes da publicação.
- Segurança, LGPD, auditabilidade e rastreabilidade são requisitos transversais.

## Como validar localmente

```powershell
$env:PYTHONPATH='tools/certification/src;services/query-service/src;services/regulatory-service/src;data/databricks/src'
python -m pytest tests -q --ignore=tests/performance/test_regulatory_100k.py --ignore=tests/performance/test_shadow_tax_100k.py
```

O último gate local registrou 86 testes Python aprovados, quatro serviços JVM aprovados, typecheck/build Next.js aprovados, contratos de observabilidade aprovados e validação Terraform do módulo de certificação. Providers cloud, Databricks workspace, E2E, performance hospedada e aprovações humanas permanecem `BLOCKED`. Não declarar a plataforma `Built` ou `Shipped` antes da matriz de certificação completa.

## Estado dos módulos

- Implementados localmente: ingestão sintética, Tax Readiness, Tax Simulation/Rules, Payment/Split, Digital Twin, Shadow Tax/Reconciliation, Regulatory AI/Copilot, Control Tower base, multi-tenancy/IaC e certificação.
- Parciais: Real-Time Engine, Bank Readiness, Fiscal Mirror, Migration Journey/Command Center, IA de capital de giro, timeline/simulador temporal e Control Tower consolidada.
- Não iniciados como produtos próprios: simulador bancário completo, Supplier/Customer Readiness, Smart Pricing e Tax Profitability.
- Fonte detalhada: `docs/MODULES_STATUS.md`.

---

## Agentes recomendados (agentcode)

| Agente | Quando usar |
|--------|-------------|
| `@brainstorm-agent` | Refinar escopo, proposta de valor e alternativas do MVP |
| `@the-planner` | Transformar a visão em fases, entregas e critérios de aceite |
| `@design-agent` | Projetar arquitetura, serviços, eventos e interfaces |
| `@aws-data-architect` | Desenhar a plataforma de dados e infraestrutura na AWS |
| `@databricks-spark-expert` | Projetar lakehouse, pipelines e processamento analítico |
| `@especialista-tributario` | Avaliar requisitos e riscos do domínio tributário brasileiro |
| `@ecc-security-reviewer` | Revisar segurança, privacidade, segredos e superfícies de ataque |
| `@code-reviewer` | Revisar implementações quando o desenvolvimento começar |

## Comandos úteis

| Comando | Quando usar |
|---------|-------------|
| `/brainstorm` | Explorar e priorizar o MVP |
| `/define` | Formalizar requisitos e critérios de aceite |
| `/design` | Criar a arquitetura técnica |
| `/party` | Obter análise paralela de múltiplas perspectivas |
| `/preflight` | Validar prontidão antes de implementar ou publicar |
| `/status` | Consultar o estado do trabalho |

---

_Gerado por `/start` em 14 de agosto de 2026._
