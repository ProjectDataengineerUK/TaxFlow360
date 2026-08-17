# DESIGN: Plataforma TaxFlow 360

> Technical design for implementing Plataforma TaxFlow 360

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | PLATAFORMA_TAXFLOW_360 |
| **Date** | 2026-08-14 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_PLATAFORMA_TAXFLOW_360.md](./DEFINE_PLATAFORMA_TAXFLOW_360.md) |
| **Status** | Ready for Build |

---

## Delivery Decomposition

Este documento passa a ser o **Design mestre** da plataforma. A implementação será governada por Designs de onda independentes, cada um com manifesto, testes e gate de Build próprios:

| Wave | Design Artifact | Scope | State |
|------|-----------------|-------|-------|
| 1 — Foundation | `DESIGN_FOUNDATION_TAXFLOW_360.md` | Contratos, tenancy, ingestão sintética, configuração, testes e CI | Build local completo; gates externos pendentes |
| 2 — Readiness | `DESIGN_READINESS_TAXFLOW_360.md` | Lakehouse mínimo, qualidade e Tax Readiness Score | Build local completo; gates externos pendentes |
| 3 — Tax Simulation | `DESIGN_TAX_SIMULATION_TAXFLOW_360.md` | Tax/Rules Engine, CBS/IBS, split simulado e fontes oficiais obrigatórias | Ready for Build |
| 4 — Digital Twin | `DESIGN_DIGITAL_TWIN_TAXFLOW_360.md` | Caixa, perda de float, capital de giro e stress | Ready for Build |
| 5 — Shadow Tax | `DESIGN_SHADOW_TAX_TAXFLOW_360.md` | Streaming, conciliação, divergências e revisão humana | Ready for Build |
| 6 — Ecosystem | `DESIGN_REGULATORY_AI_ECOSYSTEM_TAXFLOW_360.md` | Regulatory AI, base documental/vetorial com fontes oficiais, Copilot e módulos complementares | Ready for Build |
| 7 — Integration & Certification | `DESIGN_PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360.md` | E2E, runtimes hospedados, segurança, multi-cloud e release candidate | Ready for Build |
| 7.1 — Local Runtime Enablement | `DESIGN_LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360.md` | Java/Gradle, Node, Terraform, Databricks CLI e gates locais | Ready for Build |

O código criado pelo Build v1.0 não foi modificado nesta iteração. Ele deverá ser reconciliado e verificado por cada Build de onda. Essa cascata ficou explicitamente pendente por decisão do usuário.

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              TAXFLOW 360                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ XML/CSV/XLSX   ERP/PDV   E-commerce   Open Finance   Bancos/PSPs   Fisco    │
│      └───────────────┬───────────────┬───────────────┬───────────────┘       │
│                      ▼                                                       │
│        [WAF/API Gateway] → [Identity + Tenant Context]                       │
│                      ▼                                                       │
│  ┌──────────────────────────── TRANSACTION PLANE ─────────────────────────┐  │
│  │ Ingestion │ Tax/Rules │ Payment/Split │ Reconciliation │ Audit Ledger │  │
│  │    │            │             │                │              │        │  │
│  │    └────────────┴────── PostgreSQL + Redis ─────┴──────────────┘        │  │
│  └───────────────────────────────┬─────────────────────────────────────────┘  │
│                                  ▼                                            │
│                    [Kafka + Schema Registry + DLQ]                            │
│                                  ▼                                            │
│  ┌──────────────────────────── DATA / AI PLANE ───────────────────────────┐  │
│  │ Object Storage → Bronze → Silver → Gold → Semantic/Data Products      │  │
│  │                   Databricks + Delta Lake + Unity Catalog              │  │
│  │ Readiness │ Simulator │ Digital Twin │ Shadow Tax │ Regulatory AI     │  │
│  └───────────────────────────────┬─────────────────────────────────────────┘  │
│                                  ▼                                            │
│                  [Query APIs + Next.js Control Tower]                         │
│                                  │                                            │
│              Fiscal │ Financeiro │ Contábil │ Banco │ Consultoria │ Auditor  │
├──────────────────────────────────────────────────────────────────────────────┤
│ Cloud adapters: AWS | Azure | GCP     IaC: Terraform     Data/AI: Bundles     │
│ Cross-cutting: RBAC/ABAC | OTel | encryption | audit | policy | FinOps        │
└──────────────────────────────────────────────────────────────────────────────┘
```

O sistema usa arquitetura orientada a eventos com duas zonas de consistência. O plano transacional mantém cálculos determinísticos, estado operacional e auditoria. O plano de dados/IA consome eventos versionados e executa análises massivas sem participar do caminho crítico da venda. Dependências entre serviços são unidirecionais via APIs e eventos; nenhum serviço importa código de outro deployable.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Edge Gateway | WAF, rate limit, roteamento, autenticação e propagação de contexto | Gateway gerenciado por cloud + OpenAPI |
| Identity/Tenant Service | Organizações, CNPJs, usuários, papéis, consentimentos e políticas | Kotlin, Spring Boot, PostgreSQL, OIDC |
| Ingestion Service | Upload, parsing, validação, quarentena e normalização para envelope canônico | Python, FastAPI, Pydantic, streaming de arquivos |
| Tax/Rules Service | Regras versionadas, vigência, cálculo determinístico e memória de cálculo | Kotlin, Spring Boot, PostgreSQL |
| Payment/Split Service | Simulação por meio de pagamento, parcelas, split, estornos e devoluções | Kotlin, Spring Boot, PostgreSQL |
| Reconciliation Service | Conciliação de quatro pontas e ciclo de divergências | Kotlin, Spring Boot, PostgreSQL |
| Audit Ledger | Registro append-only de decisões, aprovações e reprocessamentos | PostgreSQL particionado + object lock/WORM |
| Event Backbone | Integração assíncrona, replay e fan-out | Kafka compatível + Schema Registry |
| Synthetic Data Generator | Fixtures determinísticas em três perfis de carga | Python, Faker/Hypothesis, Parquet/XML/CSV/XLSX |
| Lakehouse | Histórico, transformação, simulação e produtos analíticos | Databricks, Delta Lake, Unity Catalog, Lakeflow |
| Readiness Engine | Score explicável por dimensão, risco e evidência | Python/PySpark + regras configuradas |
| Tax Simulator | Reprocessamento temporal e comparação de cenários | PySpark + chamadas/lógica validada contra Tax Engine |
| Digital Twin | Fluxo de caixa, capital de giro, stress, preço e rentabilidade | PySpark, MLflow |
| Shadow Tax | Comparação atual/futuro e investigação de divergências | Lakeflow streaming + Delta CDF |
| Regulatory AI | Detectar mudança, gerar proposta e exigir aprovação humana | Python, model gateway, RAG, guardrails |
| Query API | Consultas agregadas, relatórios e exportações | Python, FastAPI, Databricks SQL/PostgreSQL |
| Control Tower | Experiência por persona e administração | Next.js, React, TypeScript |
| Cloud Platform | Rede, compute, dados, eventos, segredos e observabilidade por provedor | Terraform + Kubernetes/ECS-equivalent adapters |

---

## Key Decisions

### Decision 1: Separar plano transacional do plano de dados e IA

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** Cálculos de venda e split exigem baixa latência, determinismo e disponibilidade; simulações históricas e Digital Twin exigem processamento distribuído.

**Choice:** Executar Tax, Payment/Split, Reconciliation e Audit em serviços transacionais. Usar Databricks exclusivamente para lakehouse, simulações massivas, analytics, ML e IA. Integrar os planos por eventos e contratos versionados.

**Rationale:** Evita colocar o caminho crítico operacional em uma plataforma analítica, permite replay e mantém o Databricks no workload em que ele agrega mais valor.

**Alternatives Rejected:**
1. Todo cálculo no Databricks — latência e acoplamento inadequados ao caminho transacional.
2. Todo analytics no PostgreSQL — escala e custo inadequados para 100 milhões de transações e múltiplos cenários.

**Consequences:**
- A plataforma passa a operar consistência eventual entre os planos.
- Contratos, idempotência, outbox e reconciliação tornam-se obrigatórios.
- O núcleo tributário pode ser testado sem cloud ou Databricks.

---

### Decision 2: Kotlin no domínio transacional e Python/PySpark em ingestão, dados e IA

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** O domínio exige tipos monetários seguros e serviços resilientes; parsing, geração sintética, Spark e IA possuem ecossistema superior em Python.

**Choice:** Kotlin/JVM com decimal exato e tempo explícito nos engines; Python tipado com Pydantic em ingestão/query; PySpark no Databricks.

**Rationale:** Mantém cada linguagem no seu melhor contexto sem criar biblioteca de domínio compartilhada entre runtimes. O contrato canônico é a fronteira.

**Alternatives Rejected:**
1. Python em todos os serviços — viável, mas menos alinhado ao core transacional enterprise escolhido no contexto.
2. JVM em toda a plataforma — aumenta atrito com Databricks, dados sintéticos e IA.

**Consequences:**
- CI precisa validar dois ecossistemas.
- Casos dourados e contract tests garantem equivalência entre implementações.

---

### Decision 3: Multi-cloud por contratos e adaptadores, não pelo menor denominador comum

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** AWS, Azure e GCP devem produzir resultados equivalentes, mas possuem serviços e identidades diferentes.

**Choice:** Código de domínio cloud-neutral; adaptadores por provedor para gateway, identidade, storage, Kafka, PostgreSQL, segredos e observabilidade. Terraform provisiona infraestrutura; Declarative Automation Bundles promovem jobs e pipelines Databricks.

**Rationale:** Preserva semântica única e permite usar capacidades gerenciadas sem duplicar o produto.

**Alternatives Rejected:**
1. Três implementações nativas completas — risco alto de drift funcional.
2. Operar toda a infraestrutura manualmente — custo operacional desnecessário.

**Consequences:**
- Toda cloud precisa passar pela mesma suíte de paridade.
- Disponibilidade regional é gate de implantação, não pressuposto global.

---

### Decision 4: Eventos idempotentes com outbox e contratos compatíveis

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** Entrega Kafka é no mínimo uma vez em caminhos comuns; efeitos financeiros não podem duplicar.

**Choice:** Transactional outbox em cada produtor transacional, `event_id` e chave idempotente, commit manual do consumidor, inbox/dedup por serviço, Schema Registry e DLQ/quarentena separadas.

**Rationale:** O padrão local de Kafka recomenda produtores idempotentes, commit após sucesso e DLQ. Outbox fecha a lacuna entre banco e publicação.

**Alternatives Rejected:**
1. Dual write direto banco + Kafka — pode perder ou duplicar eventos em falhas parciais.
2. Confiar apenas em exactly-once do broker — não protege efeitos externos ou bancos independentes.

**Consequences:**
- Eventos carregam `event_id`, `tenant_id`, `schema_version`, correlação e instante.
- Reprocessamento é seguro e observável.

---

### Decision 5: Regras como dados versionados com aprovação em quatro olhos

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** Alterações tributárias precisam de vigência, fundamento, autoria, teste e aprovação humana.

**Choice:** Armazenar regra imutável por versão; mudanças criam nova versão em rascunho, passam por validação e aprovação de pessoa diferente antes de ativação.

**Rationale:** Permite reconstruir qualquer cálculo histórico e impede que Regulatory AI altere produção diretamente.

**Alternatives Rejected:**
1. Regras hardcoded no deploy — dificulta vigência e auditoria.
2. Atualização automática por IA — risco regulatório e de alucinação.

**Consequences:**
- Publicação de regra é evento auditado.
- Correções retroativas geram reprocessamento explícito, nunca sobrescrita silenciosa.

---

## File Manifest

O Build será executado em ondas dependentes. Cada onda deve ficar verde antes da seguinte.

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `README.md` | Create | Setup, arquitetura e comandos | @ecc-code-architect | None |
| 2 | `docs/architecture/system-context.md` | Create | Contexto, containers e limites | @ecc-architect | None |
| 3 | `contracts/events/tax-transaction.avsc` | Create | Envelope canônico de evento | @pipeline-architect | None |
| 4 | `contracts/data/tax-transaction.contract.yaml` | Create | Contrato ODCS, qualidade e SLA | @data-quality-analyst | None |
| 5 | `contracts/api/openapi.yaml` | Create | Contrato externo inicial | @ecc-code-architect | None |
| 6 | `config/platform.yaml` | Create | Configuração sem segredos | (general) | None |
| 7 | `services/tenant-service/build.gradle.kts` | Create | Build isolado do serviço | @ecc-kotlin-build-resolver | None |
| 8 | `services/tenant-service/src/main/kotlin/taxflow/tenant/Application.kt` | Create | API de tenants e RBAC | @ecc-kotlin-reviewer | 4, 5, 7 |
| 9 | `services/tenant-service/src/main/resources/db/migration/V1__tenant.sql` | Create | Schema e isolamento | @data-platform-security | 7 |
| 10 | `services/tax-service/build.gradle.kts` | Create | Build isolado do Tax Engine | @ecc-kotlin-build-resolver | None |
| 11 | `services/tax-service/src/main/kotlin/taxflow/tax/domain/TaxRule.kt` | Create | Regra imutável e vigência | @ecc-kotlin-reviewer | 10 |
| 12 | `services/tax-service/src/main/kotlin/taxflow/tax/domain/TaxCalculator.kt` | Create | Cálculo determinístico | @especialista-tributario | 11 |
| 13 | `services/tax-service/src/main/kotlin/taxflow/tax/Application.kt` | Create | API e outbox do Tax Engine | @ecc-kotlin-reviewer | 3, 5, 10-12 |
| 14 | `services/tax-service/src/main/resources/db/migration/V1__tax.sql` | Create | Regras, cálculo, memória e outbox | @databricks-sql-expert | 10 |
| 15 | `services/payment-service/build.gradle.kts` | Create | Build isolado de payment/split | @ecc-kotlin-build-resolver | None |
| 16 | `services/payment-service/src/main/kotlin/taxflow/payment/Application.kt` | Create | Simulação, estorno e devolução | @ecc-kotlin-reviewer | 3, 5, 15 |
| 17 | `services/reconciliation-service/build.gradle.kts` | Create | Build isolado da conciliação | @ecc-kotlin-build-resolver | None |
| 18 | `services/reconciliation-service/src/main/kotlin/taxflow/reconciliation/Application.kt` | Create | Four-way match e divergências | @ecc-kotlin-reviewer | 3, 5, 17 |
| 19 | `services/ingestion-service/pyproject.toml` | Create | Dependências e ferramentas isoladas | @python-developer | None |
| 20 | `services/ingestion-service/src/taxflow_ingestion/models.py` | Create | Validação do envelope canônico | @python-developer | 3, 4, 19 |
| 21 | `services/ingestion-service/src/taxflow_ingestion/parsers.py` | Create | Parsers XML/CSV/XLSX plugáveis | @python-developer | 20 |
| 22 | `services/ingestion-service/src/taxflow_ingestion/api.py` | Create | Upload, quarentena e publicação | @python-developer | 5, 20, 21 |
| 23 | `services/query-service/pyproject.toml` | Create | Dependências do Query API | @python-developer | None |
| 24 | `services/query-service/src/taxflow_query/api.py` | Create | Score, relatórios e projeções | @python-developer | 5, 23 |
| 25 | `apps/control-tower/package.json` | Create | Dependências do frontend | @ecc-typescript-reviewer | None |
| 26 | `apps/control-tower/src/app/layout.tsx` | Create | Shell, identidade e navegação | @ecc-typescript-reviewer | 25 |
| 27 | `apps/control-tower/src/app/dashboard/page.tsx` | Create | Control Tower por persona | @ecc-typescript-reviewer | 24-26 |
| 28 | `data/synthetic/pyproject.toml` | Create | Gerador determinístico | @python-developer | None |
| 29 | `data/synthetic/src/generator.py` | Create | Perfis 100k/10M/100M | @test-generator | 3, 4, 28 |
| 30 | `data/databricks/databricks.yml` | Create | Bundle multiambiente | @lakehouse-architect | None |
| 31 | `data/databricks/resources/pipelines.yml` | Create | Lakeflow Bronze/Silver/Gold | @lakeflow-architect | 30 |
| 32 | `data/databricks/src/bronze.py` | Create | Ingestão append-only com metadados | @databricks-spark-expert | 3, 31 |
| 33 | `data/databricks/src/silver.py` | Create | Validação, dedup e normalização | @databricks-spark-expert | 4, 32 |
| 34 | `data/databricks/src/gold_readiness.py` | Create | Score e evidências | @databricks-spark-expert | 33 |
| 35 | `data/databricks/src/gold_simulator.py` | Create | Cenários tributários temporais | @databricks-spark-expert | 33 |
| 36 | `data/databricks/src/gold_digital_twin.py` | Create | Caixa e stress tests | @databricks-spark-expert | 33 |
| 37 | `data/databricks/src/gold_shadow_tax.py` | Create | Comparação e divergências | @spark-streaming-architect | 33 |
| 38 | `data/databricks/src/regulatory_ai.py` | Create | Propostas regulatórias com guardrails | @genai-architect | 33 |
| 39 | `deploy/terraform/modules/platform/variables.tf` | Create | Interface comum de plataforma | @ecc-code-architect | None |
| 40 | `deploy/terraform/aws/main.tf` | Create | Recursos AWS e Databricks | @aws-data-architect | 39 |
| 41 | `deploy/terraform/azure/main.tf` | Create | Recursos Azure e Databricks | @ecc-code-architect | 39 |
| 42 | `deploy/terraform/gcp/main.tf` | Create | Recursos GCP e Databricks | @gcp-data-architect | 39 |
| 43 | `deploy/terraform/tests/platform.tftest.hcl` | Create | Contratos e mocks de IaC | @test-generator | 39-42 |
| 44 | `tests/contract/test_data_contracts.py` | Create | Compatibilidade de schemas | @data-quality-analyst | 3, 4 |
| 45 | `tests/golden/test_tax_cases.py` | Create | Acurácia e memória de cálculo | @especialista-tributario | 12, 29 |
| 46 | `tests/integration/test_ingestion_flow.py` | Create | Entrada, quarentena e eventos | @test-generator | 19-22, 29 |
| 47 | `tests/integration/test_reconciliation.py` | Create | Idempotência e four-way match | @test-generator | 16-18, 29 |
| 48 | `tests/security/test_tenant_isolation.py` | Create | Negativas de acesso cross-tenant | @ecc-security-reviewer | 8, 9, 22, 24 |
| 49 | `tests/parity/test_multicloud_parity.py` | Create | Equivalência entre clouds | @test-generator | 40-43, 45 |
| 50 | `tests/performance/test_load_profiles.py` | Create | Gates 100k/10M/100M | @spark-performance-analyzer | 29, 32-37 |
| 51 | `.github/workflows/ci.yml` | Create | Lint, unit, contract, SAST e build | @ecc-code-architect | 1-50 |
| 52 | `.github/workflows/deploy.yml` | Create | Promoção por ambiente com aprovação | @aws-deployer | 30, 39-43, 51 |

**Total Files:** 52

---

## Agent Assignment Rationale

> Agents discovered from `.claude/agents/` - Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @ecc-architect / @ecc-code-architect | 1, 2, 5, 39, 41, 51 | Limites, contratos, arquitetura e CI |
| @data-quality-analyst | 4, 44 | ODCS, qualidade, compatibilidade e evidências |
| @ecc-kotlin-build-resolver / @ecc-kotlin-reviewer | 7-18 | Serviços Kotlin isolados, domínio e build Gradle |
| @especialista-tributario | 12, 45 | Semântica tributária e casos dourados |
| @data-platform-security / @ecc-security-reviewer | 9, 48 | Isolamento, políticas e testes negativos |
| @python-developer | 19-24, 28 | Parsing, Pydantic, APIs e geração de dados |
| @ecc-typescript-reviewer | 25-27 | Next.js/React e qualidade TypeScript |
| @lakehouse-architect / @lakeflow-architect | 30, 31 | Bundle, Unity Catalog e pipelines |
| @databricks-spark-expert | 32-36 | Delta, PySpark e workloads analíticos |
| @spark-streaming-architect | 37 | Shadow Tax em streaming |
| @genai-architect | 38 | RAG, guardrails e aprovação humana |
| @aws-data-architect / @gcp-data-architect / @aws-deployer | 40, 42, 52 | Infraestrutura e implantação cloud |
| @test-generator / @spark-performance-analyzer | 29, 43, 46, 47, 49, 50 | Fixtures, integração, paridade e carga |
| @databricks-sql-expert | 14 | Schema transacional e consultas auditáveis |
| (general) | 6 | Configuração simples sem especialista necessário |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: File type, purpose keywords, path patterns, KB domains

---

## Code Patterns

### Pattern 1: Valor monetário e regra temporal determinísticos

```kotlin
package taxflow.tax.domain

import java.math.BigDecimal
import java.math.RoundingMode
import java.time.Instant

data class TaxRule(
    val id: String,
    val version: String,
    val validFrom: Instant,
    val validUntil: Instant?,
    val rate: BigDecimal,
    val legalBasis: String,
) {
    fun appliesAt(occurredAt: Instant): Boolean =
        !occurredAt.isBefore(validFrom) &&
            (validUntil == null || occurredAt.isBefore(validUntil))
}

data class TaxResult(
    val baseAmount: BigDecimal,
    val taxAmount: BigDecimal,
    val ruleId: String,
    val ruleVersion: String,
)

fun calculateTax(baseAmount: BigDecimal, rule: TaxRule, occurredAt: Instant): TaxResult {
    require(baseAmount.signum() >= 0) { "baseAmount must be non-negative" }
    require(rule.appliesAt(occurredAt)) { "rule is not effective at occurredAt" }
    val tax = baseAmount.multiply(rule.rate).setScale(2, RoundingMode.HALF_EVEN)
    return TaxResult(baseAmount, tax, rule.id, rule.version)
}
```

### Pattern 2: Envelope canônico validado e idempotente

```python
from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TaxTransaction(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID
    tax_transaction_id: str = Field(min_length=1)
    tenant_id: UUID
    source_system: str = Field(min_length=1)
    source_event_id: str = Field(min_length=1)
    occurred_at: datetime
    operation_amount: Decimal = Field(ge=Decimal("0"), max_digits=20, decimal_places=2)
    currency: Literal["BRL"] = "BRL"
    schema_version: str = Field(pattern=r"^[1-9]\d*\.\d+\.\d+$")

    @property
    def idempotency_key(self) -> str:
        return f"{self.tenant_id}:{self.source_system}:{self.source_event_id}"
```

### Pattern 3: Configuration Structure

```yaml
platform:
  environment: local
  cloud: local
  default_currency: BRL

events:
  schema_compatibility: backward
  manual_commit: true
  dead_letter_suffix: .dlq
  max_retries: 5

tenancy:
  require_tenant_context: true
  deny_cross_tenant_by_default: true

tax:
  rounding_mode: HALF_EVEN
  monetary_scale: 2
  require_four_eyes_approval: true

data:
  bronze_mode: append
  synthetic_profiles:
    small: 100000
    medium: 10000000
    enterprise: 100000000
```

---

## Data Flow

```text
1. Fonte envia arquivo, API call ou evento
   │
   ▼
2. Edge autentica; Tenant Service resolve tenant, CNPJ, papéis e política
   │
   ▼
3. Ingestion valida contrato, normaliza e atribui Tax Transaction ID
   ├── inválido → quarentena + evidência + métrica
   └── válido   → persistência + transactional outbox
   │
   ▼
4. Kafka publica envelope versionado; consumidores usam inbox/idempotência
   │
   ├── Tax/Rules calcula e emite memória de cálculo
   ├── Payment/Split simula liquidação
   ├── Reconciliation correlaciona quatro pontas
   └── Audit Ledger registra decisões e aprovações
   │
   ▼
5. Eventos e arquivos aterrissam no storage; Lakeflow ingere Bronze append-only
   │
   ▼
6. Silver valida, deduplica, protege PII e preserva histórico/linhagem
   │
   ▼
7. Gold produz Readiness, cenários, Digital Twin, Shadow Tax e produtos de IA
   │
   ▼
8. Query API aplica tenant/política e publica resultados no Control Tower
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| ERP/PDV/e-commerce | REST, webhook, SFTP, arquivos | OAuth 2.0/OIDC, mTLS ou chave rotacionada por conector |
| Open Finance | APIs padronizadas | OAuth 2.0, mTLS, consentimento e certificados aplicáveis |
| Bancos e PSPs | REST, eventos e arquivos de conciliação | OAuth 2.0/mTLS e credenciais institucionais |
| Sistemas fiscais | API/exportação | Método do fornecedor, encapsulado pelo conector |
| Kafka compatível | Producer/consumer + Schema Registry | Identidade de workload, TLS e ACL por tópico |
| Databricks | Terraform, Bundles, SQL/Jobs APIs | OAuth de service principal/workload identity |
| Cloud object storage | SDK e Auto Loader | Workload identity sem chaves estáticas |
| Provedor OIDC | OIDC/SAML federation | MFA, SSO e conditional access |
| Model providers | Gateway compatível e allowlist | Workload identity ou segredo gerenciado; sem credencial no código |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Regras, arredondamento, vigência, parsers e scores | Testes ao lado de cada serviço/pipeline | JUnit 5, Kotest, pytest, Hypothesis, Vitest | ≥90% no domínio crítico; ≥80% geral |
| Contract | Avro, ODCS, OpenAPI e compatibilidade | `tests/contract/` | datacontract-cli, Avro compatibility, Schemathesis | 100% dos contratos publicados |
| Golden | CBS/IBS, split e memória | `tests/golden/` | pytest/JUnit + datasets aprovados | ≥99,5% de acurácia; 100% dos casos críticos |
| Integration | API, PostgreSQL, Kafka, storage e Databricks | `tests/integration/` | Testcontainers, LocalStack/emuladores, Databricks test workspace | Todos os caminhos e falhas principais |
| Security | RBAC/ABAC, tenant, PII, secrets, SAST/DAST | `tests/security/` | pytest, ZAP, Semgrep, dependency/secret scan | Zero bypass cross-tenant e zero crítico aberto |
| E2E | AT-001 a AT-015 | Suíte orquestrada CI/staging | Playwright + APIs + datasets sintéticos | 100% dos acceptance tests |
| Parity | Mesmo cálculo nas três clouds | `tests/parity/` | Runner determinístico e checksums | 100% de equivalência semântica |
| Performance | 100k, 10M e 100M; API e streaming | `tests/performance/` | k6, pytest-benchmark, Spark metrics | Cumprir SLO da fase sem perda/duplicação |
| Resilience | Retry, DLQ, replay, failover e dependência indisponível | Cenários de chaos em staging | Toxiproxy/chaos tooling | Recuperação sem efeito duplicado |
| IaC | Plan, policy e módulos | `deploy/terraform/tests/` | terraform fmt/validate/test, Checkov/tfsec | 100% dos módulos e políticas críticas |

Mapeamento: AT-001/002/013 usam ingestão e carga; AT-003/004/010 usam golden; AT-005/006 usam pipelines; AT-007/009 usam integração; AT-008 usa segurança; AT-011/015 usam auditoria/governança; AT-012 usa paridade; AT-014 usa resiliência.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Schema ou regra inválida | Rejeitar/quarentenar com código, campo, versão e correlação | No |
| Dependência temporariamente indisponível | Backoff exponencial com jitter e circuit breaker | Yes, bounded |
| Evento duplicado | Inbox/idempotency key; retornar resultado anterior | No effect |
| Poison message | DLQ com payload protegido, erro e origem; replay autorizado | Manual/controlled |
| Regra ausente para vigência | Não calcular; abrir pendência explicável | No |
| Divergência de ground truth | Bloquear promoção e encaminhar à revisão humana | No |
| Falha parcial de publicação | Transactional outbox retenta até confirmação | Yes |
| Conflito de concorrência | Optimistic locking e retry limitado | Yes, bounded |
| Violação cross-tenant | Negar, auditar e alertar segurança | No |
| Falha de pipeline/SLA | Preservar checkpoint, alertar e retomar idempotentemente | Yes, bounded |
| Saída de IA sem evidência | Bloquear/rotular como insuficiente e exigir revisão | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `platform.environment` | string | `local` | Ambiente lógico |
| `platform.cloud` | enum | `local` | `local`, `aws`, `azure` ou `gcp` |
| `events.schema_compatibility` | enum | `backward` | Política de evolução |
| `events.max_retries` | int | `5` | Limite antes da DLQ |
| `tenancy.require_tenant_context` | bool | `true` | Bloqueia requisição sem tenant |
| `tax.rounding_mode` | enum | `HALF_EVEN` | Arredondamento monetário explícito |
| `tax.monetary_scale` | int | `2` | Escala padrão em BRL |
| `tax.require_four_eyes_approval` | bool | `true` | Separa autor e aprovador |
| `data.bronze_mode` | enum | `append` | Preserva entrada bruta |
| `data.synthetic_profile` | enum | `small` | Volume do dataset sintético |
| `observability.trace_sample_rate` | decimal | `0.1` | Amostragem ajustável, nunca remove auditoria |

Segredos, hosts e credenciais não pertencem ao YAML; vêm do secret manager e da identidade de workload de cada cloud.

---

## Security Considerations

- Tenant context é derivado de identidade confiável, nunca aceito apenas do corpo da requisição.
- Defesa em profundidade: gateway, autorização no serviço, row-level policy, prefixos/buckets, catálogos e logs segregados.
- Criptografia em trânsito e repouso; chaves e retenção configuradas por classificação e jurisdição.
- CNPJ, chaves fiscais e dados pessoais são classificados, tokenizados/mascarados fora de produção e minimizados.
- Service principals usam menor privilégio e workload identity; chaves estáticas são proibidas quando houver federação.
- Audit Ledger é append-only com retenção e cópia WORM; logs não armazenam payload fiscal integral nem segredos.
- Publicação de regra exige separação de funções, assinatura lógica e aprovação em quatro olhos.
- Regulatory AI usa RAG apenas em fontes aprovadas, validação de entrada/saída, allowlist de ferramentas e nenhuma escrita produtiva direta.
- Dependências, imagens e IaC passam por SBOM, assinatura, SAST, SCA, secret scan e policy-as-code.
- Backups, restauração, RPO/RTO e resposta a incidentes são testados por ambiente antes de dados reais.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | JSON estruturado com `tenant_id` pseudonimizado, `tax_transaction_id`, `event_id`, regra, serviço e severidade; sem payload sensível |
| Metrics | Taxa, latência, erro, retry, DLQ, quarentena, lag Kafka, freshness, score, conciliação e custo por tenant/cloud |
| Tracing | OpenTelemetry com W3C Trace Context propagado por HTTP e Kafka |
| Audit | Ledger separado de logs operacionais, append-only e consultável por autorização específica |
| Alerting | SLO burn rate, falha de qualidade, drift de paridade, cross-tenant e divergência crítica |
| Data observability | Linhagem Unity Catalog, expectativas Lakeflow, contagem/checksum entre camadas e freshness |

---

## Pipeline Architecture (if applicable)

> Include this section when the feature involves data pipelines, ETL, or analytics.

### DAG Diagram

```text
[XML/CSV/XLSX] ─parse──┐
[APIs/Webhooks] ───────┼→ [Landing/Object Storage] → [Bronze append-only]
[Kafka Events] ────────┘             │                       │
                                     └→ [Archive/WORM]       ▼
                                                   [Contract + DQ Gate]
                                                         │
                                              invalid → [Quarantine]
                                                         │ valid
                                                         ▼
                                              [Silver canonical + history]
                                                │       │       │
                                                ▼       ▼       ▼
                                          [Readiness] [Twin] [Shadow/Recon]
                                                └───────┬───────┘
                                                        ▼
                                              [Gold + Semantic Products]
                                                        ▼
                                               [Query API/Dashboards]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|-------------|-------------|-----------|
| Bronze transactions | `ingestion_date` | Daily | Replay e manutenção por lote sem usar cardinalidade alta |
| Silver transactions | `occurred_date` | Monthly/daily conforme volume | Consultas temporais; liquid clustering por `tenant_id`, `company_tax_id` e ID |
| Tax calculations | `calculation_date` | Monthly | Auditoria e recomputação temporal |
| Reconciliation facts | `settlement_date` | Monthly | Fechamento por período e instituição |
| Shadow divergences | `detected_date` | Daily | Investigação operacional e SLA |
| Gold readiness | `assessment_date` | Monthly/snapshot | Histórico de score por tenant/CNPJ |
| Cash-flow scenarios | `scenario_month` | Monthly | Séries temporais e comparação de cenários |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Bronze | Append-only + checkpoint | `event_id` | Replay por checkpoint/lote |
| Silver canonical | MERGE idempotente | `tenant_id`, `source_system`, `source_event_id` | 7 dias configuráveis |
| Rules dimension | SCD Type 2 / versão imutável | `rule_id`, `version` | Vigência integral |
| Tax calculations | Append de nova versão; sem overwrite | `calculation_id` | Reprocessamento explícito |
| Reconciliation | MERGE por identidade transacional | `tax_transaction_id` | Janela conforme meio de pagamento |
| Readiness Gold | Snapshot incremental | `tenant_id`, `company_tax_id`, `assessment_at` | Último ciclo + correções |
| Shadow Tax | Streaming + Delta CDF | `event_id`, `_commit_version` | Checkpoint contínuo |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| New optional column | Atualizar contrato com compatibilidade backward e dual-read | Ignorar coluna na versão anterior |
| New required column | Adicionar opcional, backfill, validar, depois exigir | Manter coluna opcional |
| Type widening | Publicar nova versão, validar consumers e habilitar widening suportado | Voltar leitura à versão anterior |
| Type narrowing | Criar coluna nova, converter, comparar e migrar | Manter coluna antiga durante depreciação |
| Rename | Dual-write/alias por janela de depreciação | Consumidores continuam usando nome antigo |
| Removal | Deprecar, medir consumidores, aprovar e remover após janela | Restaurar contrato/tabela por versão |
| Breaking event change | Novo major schema e tópico/version discriminator | Reativar consumidor do major anterior |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Contrato e tipos | Pydantic/Avro/ODCS/Lakeflow expectations | 100% dos aceitos válidos | Quarentena; bloquear Silver |
| PK/identidade | Lakeflow/dbt tests | Zero nulos e zero efeitos duplicados | Bloquear pipeline |
| Completude de ingestão | Checksums e contagens | 100% contabilizado como aceito/rejeitado/quarentena | Bloquear e alertar |
| Totais monetários | Testes de invariantes | Diferença zero além da política de arredondamento | Bloquear Gold/release |
| Acurácia tributária | Golden suite | ≥99,5%, 100% dos casos críticos | Bloquear promoção |
| Conciliação | Testes de domínio | ≥99,9% elegível | Alertar/bloquear conforme severidade |
| Freshness | Lakeflow/observability | Dentro do SLA da fase | Alertar; bloquear consumidor crítico |
| Drift de schema | CI contract diff | Zero breaking sem major/depreciação | Bloquear merge |
| Paridade cloud | Checksums/result comparison | 100% semântico | Bloquear release da cloud divergente |
| PII e tenant | Unity Catalog/policy tests | Zero exposição indevida | Bloquear e abrir incidente |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-14 | design-agent | Initial platform design derived from DEFINE v1.0 |
| 1.1 | 2026-08-14 | iterate-agent | Decomposed delivery into independent SDD waves; code cascade intentionally deferred |
| 1.2 | 2026-08-15 | define-agent | Registered completed local waves and Tax Simulation definition; external Ship gates remain open |
| 1.3 | 2026-08-15 | iterate-agent | Sequenced mandatory official-source links in Wave 3 and regulatory vector retrieval in Wave 6 |
| 1.4 | 2026-08-15 | design-agent | Completed Tax Simulation technical design and advanced Wave 3 to Ready for Build |
| 1.5 | 2026-08-17 | define-agent | Registered the Digital Twin definition and advanced Wave 4 to Ready for Design |
| 1.6 | 2026-08-17 | design-agent | Completed the Digital Twin design and advanced Wave 4 to Ready for Build |
| 1.7 | 2026-08-17 | define-agent | Registered the Shadow Tax definition and advanced Wave 5 to Ready for Design |
| 1.8 | 2026-08-17 | design-agent | Completed the Shadow Tax design and advanced Wave 5 to Ready for Build |
| 1.9 | 2026-08-17 | define-agent | Registered Regulatory AI/vector knowledge definition and advanced Wave 6 to Ready for Design |
| 2.0 | 2026-08-17 | design-agent | Completed Regulatory AI technical design and advanced Wave 6 to Ready for Build |
| 2.1 | 2026-08-17 | define-agent | Registered platform integration/certification and advanced Wave 7 to Ready for Design |
| 2.2 | 2026-08-17 | design-agent | Completed integration/certification design and advanced Wave 7 to Ready for Build |
| 2.3 | 2026-08-17 | define-agent | Registered local runtime enablement as Wave 7.1 and advanced it to Ready for Design |
| 2.4 | 2026-08-17 | design-agent | Completed local runtime enablement design and advanced Wave 7.1 to Ready for Build |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_TAX_SIMULATION_TAXFLOW_360.md`
