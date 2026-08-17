# DEFINE: Integração e Certificação da Plataforma TaxFlow 360

> Integrar todas as waves em jornadas sintéticas completas, executar gates hospedados e produzir um release candidate auditável sem antecipar deploy produtivo.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

As seis waves possuem implementação e testes locais, mas a plataforma ainda não foi certificada como um sistema integrado nos runtimes reais. Sem contratos E2E, ambientes efêmeros, gates hospedados e evidências consolidadas, não é possível promover os artefatos para `Built`, gerar um release candidate ou iniciar Ship com segurança.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Engenharia de plataforma | Opera CI/CD e ambientes | Precisa de uma sequência reproduzível para validar todos os runtimes |
| Engenharia fiscal/dados | Valida cálculo, lakehouse e RAG | Precisa provar paridade, lineage e qualidade de ponta a ponta |
| Segurança/compliance | Aprova controles e release | Precisa de isolamento, SBOM, evidências e exceções formalizadas |
| Especialista tributário | Aprova catálogo e corpus dourado | Precisa revisar regras/citações sem depender de detalhes de infraestrutura |
| QA/SRE | Certifica resiliência e SLO | Precisa de cenários, telemetria, replay, recovery e critérios de aprovação |
| Product owner | Decide go/no-go | Precisa de uma visão única do que passou, falhou ou permanece bloqueado |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Fixar versões de Java, Gradle, Node, npm, Python, Terraform, Databricks CLI e dependências em CI reproduzível |
| **MUST** | Validar contratos ODCS, Avro, OpenAPI, eventos, schemas e compatibilidade entre todas as waves |
| **MUST** | Executar jornada E2E sintética: ingestão → readiness → simulação → Digital Twin → Shadow Tax → Regulatory AI |
| **MUST** | Executar testes JVM, Python, Next/TypeScript, Terraform e Databricks em runtimes hospedados aprovados |
| **MUST** | Provar isolamento tenant/CNPJ em API, banco, eventos, cache, storage, lakehouse, busca vetorial, logs e métricas |
| **MUST** | Provar idempotência, replay, eventos tardios, outbox, rollback e recuperação sem efeito financeiro/fiscal real |
| **MUST** | Provar que todo cálculo/resposta tributária mantém regra, memória, versão e link oficial verificável |
| **MUST** | Executar gates de segurança: SAST, SCA, secret scan, SBOM, IaC scan, imagem, RLS e ataques RAG |
| **MUST** | Executar performance progressiva em 100 mil e preparar gates separados de 10 milhões/100 milhões |
| **MUST** | Validar Terraform e adapters em AWS, Azure e GCP sem exigir produção simultânea |
| **MUST** | Validar Databricks streaming, CDF/checkpoints, Delta Sync AI Search, MLflow e Unity Catalog |
| **MUST** | Consolidar evidências em matriz go/no-go; nenhum gate ausente pode aparecer como aprovado |
| **MUST** | Produzir release candidate imutável, assinado e rastreável somente quando gates obrigatórios passarem |
| **SHOULD** | Executar chaos/fault injection em staging para dependências, checkpoint, banco e modelo indisponíveis |
| **COULD** | Automatizar scorecard de certificação por edição SaaS, Enterprise e Sovereign/Financial |

---

## Success Criteria

- [ ] Compilar e testar 100% dos módulos JVM, Python e TypeScript nos runtimes fixados, sem falha.
- [ ] Resolver 100% das referências OpenAPI/ODCS/Avro e impedir breaking change não versionada.
- [ ] Concluir 100% das jornadas E2E obrigatórias com dataset sintético determinístico e correlation IDs preservados.
- [ ] Bloquear 100% dos cenários cross-tenant/cross-CNPJ em todas as camadas testadas, sem disclosure.
- [ ] Obter paridade monetária de 100% entre motor transacional e lakehouse nos casos dourados, usando Decimal/HALF_EVEN.
- [ ] Preservar 100% das citações oficiais em cálculo, divergência, projeção e resposta regulatória.
- [ ] Restaurar checkpoint/replay/backup nos cenários aprovados sem duplicar efeitos nem apagar histórico.
- [ ] Atender aos SLOs das waves no perfil de 100 mil operações/chunks, sem perda silenciosa.
- [ ] Obter zero vulnerabilidade crítica, zero segredo versionado e zero falha crítica de RLS/IaC/RAG.
- [ ] Validar `terraform fmt/validate/test/plan` para AWS, Azure e GCP com providers fixados.
- [ ] Validar Databricks bundles, pipelines, CDF, streaming progress, AI Search e avaliação em workspace de teste.
- [ ] Registrar aprovação humana independente do catálogo tributário e do corpus regulatório dourado.
- [ ] Gerar SBOM, checksums, assinatura/proveniência e tag única para 100% dos artefatos do release candidate.
- [ ] Manter 100% dos gates não executados como `BLOCKED`, nunca `PASS` inferido.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| IC-AT-001 | Toolchain reproduzível | Lockfiles/tool versions definidos | CI limpa executar | Mesmos builds e checksums são produzidos ou diferenças são explicadas |
| IC-AT-002 | Compatibilidade contratual | Produtor e consumidor de cada evento/API | Contract tests executarem | Nenhum campo obrigatório/ref quebrado é publicado |
| IC-AT-003 | Jornada completa | Empresa sintética com fiscal, financeiro, pagamentos e documentos | Pipeline E2E executar | Todos os seis produtos geram resultados correlacionados e citados |
| IC-AT-004 | Tenant adversarial | Dois tenants com IDs conhecidos entre si | Suítes consultarem APIs/DB/Delta/vector/cache | Nenhum dado, contagem ou existência cruza a fronteira |
| IC-AT-005 | Paridade tributária | Casos dourados atuais/reforma/split | Kotlin e PySpark calcularem | Valores, decisões, memória e regras coincidem integralmente |
| IC-AT-006 | Replay | Eventos duplicados/tardios e checkpoint restaurado | Fluxo for reaplicado | Fingerprints e efeitos permanecem semanticamente idênticos |
| IC-AT-007 | Falha de dependência | Banco, modelo, search ou stream indisponível | Fault injection executar | Circuit breaker/retry/fallback atuam sem resposta inventada ou efeito duplicado |
| IC-AT-008 | Fontes oficiais | Cálculo e resposta regulatória publicados | Auditor abrir evidência | Link, documento, dispositivo e snapshot/hash são resolvíveis |
| IC-AT-009 | Segurança supply chain | Código, imagens, IaC e dependências do RC | Scanners executarem | Nenhum achado crítico/segredo; SBOM e proveniência são gerados |
| IC-AT-010 | AWS | Configuração de teste AWS aprovada | Terraform plan/test executar | Contrato de plataforma, criptografia, versionamento e identidade passam |
| IC-AT-011 | Azure | Configuração de teste Azure aprovada | Terraform plan/test executar | Mesmos invariantes portáveis passam |
| IC-AT-012 | GCP | Configuração de teste GCP aprovada | Terraform plan/test executar | Mesmos invariantes portáveis passam |
| IC-AT-013 | Databricks streaming | Workspace com CDF/checkpoints | Shadow Tax executar | Freshness, completude, late data e replay atendem gates |
| IC-AT-014 | Databricks AI Search | Índice Delta Sync e golden corpus | Avaliação executar | Recall@10, precisão de citação, ACL e p95 atendem gates |
| IC-AT-015 | Revisão tributária | Catálogo/corpus sintéticos e evidências | Especialistas independentes revisarem | Aprovação/rejeição e justificativas ficam imutáveis |
| IC-AT-016 | Performance 100k | Perfil determinístico consolidado | Jornada completa executar | SLO, contabilização, custo e recursos são registrados |
| IC-AT-017 | Backup/restore | Snapshots e bancos de staging | Procedimento de recuperação executar | RPO/RTO medidos e histórico/tenancy preservados |
| IC-AT-018 | Release candidate | Todos os gates obrigatórios verdes | Pipeline de promoção executar | Artefatos assinados, checksums, SBOM e matriz go/no-go são congelados |
| IC-AT-019 | Gate pendente | Um runtime/aprovação não está disponível | Relatório consolidar | Status final permanece `BLOCKED`; RC não é promovido |

---

## Out of Scope

Explicitly NOT included in this feature:

- Implantação produtiva, onboarding de clientes reais ou tráfego financeiro/fiscal real.
- Certificação governamental, bancária ou jurídica externa não contratada.
- Aprovação automática de regra, corpus, risco ou exceção de segurança.
- Execução automática de recursos cloud com custo sem ambiente, orçamento e autorização explícitos.
- Uso de dados pessoais, fiscais ou bancários reais.
- Gate de 10 milhões/100 milhões dentro do RC inicial; ficam preparados e separados após aprovação do perfil de 100 mil.
- Corrigir silenciosamente falha funcional descoberta; cada correção volta ao Build/teste da wave proprietária.
- Marcar Ship enquanto qualquer gate obrigatório estiver bloqueado ou com evidência incompleta.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Environment | Runtimes/credenciais externos não existem no workspace local | Design deve separar gates locais, CI e ambientes autorizados |
| Cost | Databricks e três clouds geram custo | Ambientes efêmeros, budgets e aprovação precedem apply/load |
| Safety | Apenas dados sintéticos | Fixtures e geradores determinísticos são a fonte E2E |
| Governance | Catálogo/corpus exigem especialistas independentes | Automação prepara evidência, não concede aprovação |
| Portability | Núcleo precisa manter paridade AWS/Azure/GCP | Contrato Terraform e suíte comum precedem adapters |
| Determinism | Resultados dependem de cutoff/config/model/index | Toda execução fixa e registra versões/checksums |
| Security | Zero critical e isolamento integral | Achado crítico bloqueia RC sem waiver automático |
| SDD | Waves permanecem proprietárias de seus arquivos | Integração não mascara regressão; relatório referencia wave responsável |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.tool-versions`, Gradle/npm/Python locks, `contracts/`, `deploy/`, `tests/e2e/`, `tests/conformance/`, `.github/workflows/`, `.claude/sdd/reports/` | Certificação transversal sem duplicar motores |
| **KB Domains** | `testing`, `ci-cd`, `security`, `terraform`, `spark`, `streaming`, `lakehouse`, `data-quality`, `observability` | Contract/E2E/chaos/performance/release evidence |
| **IaC Impact** | Modify existing + ephemeral test environments | Plans multi-cloud, Databricks workspace contract, budgets and teardown |

**Why This Matters:**

- **Location** → mantém código de domínio nas waves e concentra apenas orquestração/evidência transversal.
- **KB Domains** → o Design deve definir matriz de testes, ambientes, promoção e rollback.
- **IaC Impact** → nenhuma validação cloud pode ocorrer sem budget, identidade e teardown governados.

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Synthetic generator Foundation | CSV/XML/XLSX/eventos | 100 mil gate inicial | Por execução | Platform QA |
| Golden tax/readiness/twin/shadow/regulatory | YAML/Delta fixtures | Centenas de casos | Versionado por release | Domain owners |
| JVM/Python/Next test reports | JUnit/pytest/JSON | Por commit | CI | Engineering |
| Terraform plans/tests | Plan JSON/test reports | AWS/Azure/GCP por RC | Por RC | Platform engineering |
| Databricks progress/evaluation | Delta/MLflow/metrics | Streaming + RAG | Por RC | Data platform |
| Security/SBOM/provenance | SARIF/CycloneDX/SLSA-like attestations | Por artefato | Por RC | Security |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `certification_run_id` | UUID/STRING | NOT NULL, immutable | No |
| `release_candidate` | STRING | NOT NULL, semver/commit | No |
| `gate_id` | STRING | NOT NULL, unique within run | No |
| `wave` | STRING | NOT NULL | No |
| `environment` | STRING | NOT NULL | No |
| `status` | ENUM | PASS/FAIL/BLOCKED/SKIPPED_WITH_APPROVAL | No |
| `evidence_uri` | STRING | NOT NULL for PASS/FAIL | Potentially |
| `evidence_sha256` | CHAR(64) | NOT NULL for PASS/FAIL | No |
| `started_at/completed_at` | TIMESTAMP_TZ | Logical run timestamps | No |
| `approver_ids` | ARRAY<STRING> | Required for human gates | Yes |
| `tool_versions` | MAP<STRING,STRING> | NOT NULL | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Fast CI | Até 15 minutos por commit | commit → required checks |
| Hosted integration | Até 60 minutos por candidate | dispatch → evidence commit |
| Full certification | Até 24 horas após ambientes disponíveis | run start → signed matrix |

### Completeness Metrics

- 100% dos gates do RC têm status explícito e owner.
- 100% dos `PASS/FAIL` têm evidência com checksum.
- 100% dos gates humanos têm ator, papel, decisão e justificativa.
- Zero promoção com gate obrigatório `FAIL`, `BLOCKED` ou sem evidência.

### Lineage Requirements

- RC → commit/toolchain/lockfiles → builds/images/SBOM/checksums.
- Gate → ambiente/configuração/dataset/cutoff → logs/métricas/resultado.
- Jornada E2E → transaction ID → cada produto → regra/memória/fonte oficial.
- Aprovação → especialista/papel → catálogo/corpus/evidência → decisão.
- Cloud plan → provider/module/input → plan hash → policy result.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| IC-A-001 | CI poderá instalar Java 21, Gradle, Node e Terraform com versões fixas | Gates desses runtimes permanecem bloqueados | [ ] |
| IC-A-002 | Um workspace Databricks com Unity Catalog/serverless/CDF/AI Search será disponibilizado | Streaming/RAG não podem ser certificados | [ ] |
| IC-A-003 | Contas sandbox AWS/Azure/GCP com budgets estarão disponíveis | Plan/test de um ou mais adapters fica bloqueado | [ ] |
| IC-A-004 | Especialistas tributários revisarão catálogo e corpus dourado | RC não pode ser aprovado | [ ] |
| IC-A-005 | Perfil sintético de 100 mil representa o RC inicial | Novo perfil/SLO será necessário | [x] |
| IC-A-006 | GitHub Actions pode armazenar evidências e attestations exigidas | Será necessário registry/evidence store alternativo | [ ] |
| IC-A-007 | Nenhuma wave exige breaking change para integração | Descoberta volta ao Design/Build da wave proprietária | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Lacuna entre build local e certificação hospedada está explícita |
| Users | 3 | Engenharia, segurança, domínio, QA/SRE e produto identificados |
| Goals | 3 | Toolchain, E2E, clouds, Databricks, segurança e RC priorizados |
| Success | 3 | Critérios quantitativos e regra BLOCKED/PASS inequívoca |
| Scope | 3 | Certificação e RC separados de produção, dados reais e grandes cargas |
| **Total** | **15/15** | Gate de clareza atendido |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Quais contas/subscriptions/projects sandbox e regiões serão autorizados para AWS, Azure e GCP?
- Qual workspace Databricks será usado e quem aprova budget, identidade e teardown?
- Quais especialistas fiscais assinarão catálogo tributário e corpus regulatório dourado?
- Qual registry armazenará imagens, SBOM, assinaturas e attestations do release candidate?
- Quais RPO/RTO e limites de custo serão aprovados para staging/certificação?

Essas respostas são pré-condições operacionais do Build/Ship, não motivo para reduzir os gates.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | define-agent | Definição inicial da Wave 7 de integração, certificação e release candidate |
| 1.1 | 2026-08-17 | design-agent | Design técnico concluído e liberado para Build |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360.md`
