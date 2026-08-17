# DESIGN: Fundação TaxFlow 360

> Technical design for a verifiable foundation of contracts, tenancy, synthetic ingestion and delivery gates

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | FOUNDATION_TAXFLOW_360 |
| **Date** | 2026-08-14 |
| **Author** | iterate-agent |
| **DEFINE** | [DEFINE_PLATAFORMA_TAXFLOW_360.md](./DEFINE_PLATAFORMA_TAXFLOW_360.md) |
| **Parent DESIGN** | [DESIGN_PLATAFORMA_TAXFLOW_360.md](./DESIGN_PLATAFORMA_TAXFLOW_360.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
Synthetic XML/CSV/XLSX
          |
          v
 [Ingestion API] ----invalid----> [Quarantine]
          |
       valid contract
          |
          v
 [Canonical Event] ---> [Contract Test Boundary]
          |
          v
 [Tenant Context + RBAC] ---> [Audit-ready identity]

Cross-cutting: configuration without secrets, CI, deterministic fixtures
```

Esta onda prova as fronteiras que todas as ondas seguintes reutilizam: identidade de tenant, contrato canônico, parsing, idempotência, quarentena, geração sintética e gates automatizados. Não provisiona cloud nem implementa cálculo tributário.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Canonical Contracts | Versionar API, evento e dados | OpenAPI 3.1, Avro, ODCS YAML |
| Tenant Service | Tenant, CNPJ, papéis e negação cross-tenant | Kotlin, Spring Boot |
| Ingestion Service | Parse, validar, deduplicar e quarentenar | Python, FastAPI, Pydantic |
| Synthetic Generator | Criar fixtures determinísticas e perfis de volume | Python |
| Platform Configuration | Defaults seguros sem credenciais | YAML |
| Foundation Test Suite | Contratos, ingestão e isolamento | pytest/JUnit |
| CI | Reproduzir validações em ambiente hospedado | GitHub Actions |

---

## Key Decisions

### Decision 1: Contrato antes de integração

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** Fontes reais ainda não possuem sandboxes e o produto precisa aceitar múltiplos formatos sem acoplar o domínio a fornecedores.

**Choice:** Normalizar todas as entradas para um envelope canônico versionado e validar compatibilidade em CI antes de criar conectores reais.

**Rationale:** Dados sintéticos exercitam o contrato e os casos de erro com segurança, tornando conectores posteriores adaptadores substituíveis.

**Alternatives Rejected:**
1. Integrar um ERP antes de definir o contrato — transfere o modelo do fornecedor para o núcleo.
2. Aceitar payload flexível sem schema — impede qualidade, evolução e auditoria confiáveis.

**Consequences:**
- Mudanças breaking exigem nova major version.
- Todo registro termina aceito, duplicado ou em quarentena.

---

### Decision 2: Tenant derivado de identidade confiável

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** O tenant não pode ser escolhido livremente pelo payload de negócio.

**Choice:** Propagar tenant por contexto autenticado; serviços negam ausência, divergência ou acesso cruzado.

**Rationale:** Deny-by-default reduz o risco estrutural mais crítico do SaaS multi-tenant.

**Alternatives Rejected:**
1. `tenant_id` somente no corpo — adulterável pelo cliente.
2. Filtragem apenas no frontend — não constitui controle de segurança.

**Consequences:**
- Testes negativos são obrigatórios.
- O banco da onda futura deverá reforçar a mesma política.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `README.md` | Verify/Modify | Setup da Fundação | @ecc-code-architect | None |
| 2 | `docs/architecture/system-context.md` | Verify/Modify | Limites e ondas | @ecc-architect | None |
| 3 | `contracts/events/tax-transaction.avsc` | Verify/Modify | Evento canônico | @pipeline-architect | None |
| 4 | `contracts/data/tax-transaction.contract.yaml` | Verify/Modify | Contrato, qualidade e SLA | @data-quality-analyst | None |
| 5 | `contracts/api/openapi.yaml` | Verify/Modify | API pública da Fundação | @ecc-code-architect | None |
| 6 | `config/platform.yaml` | Verify/Modify | Defaults sem segredos | (general) | None |
| 7 | `services/tenant-service/build.gradle.kts` | Verify/Modify | Build isolado | @ecc-kotlin-build-resolver | None |
| 8 | `services/tenant-service/src/main/kotlin/taxflow/tenant/Application.kt` | Verify/Modify | Tenant e RBAC | @ecc-kotlin-reviewer | 5, 7 |
| 9 | `services/tenant-service/src/main/resources/db/migration/V1__tenant.sql` | Verify/Modify | Persistência e isolamento | @data-platform-security | 7 |
| 10 | `services/ingestion-service/pyproject.toml` | Verify/Modify | Dependências isoladas | @python-developer | None |
| 11 | `services/ingestion-service/src/taxflow_ingestion/models.py` | Verify/Modify | Envelope Pydantic | @python-developer | 3, 4, 10 |
| 12 | `services/ingestion-service/src/taxflow_ingestion/parsers.py` | Verify/Modify | CSV/XML/XLSX | @python-developer | 11 |
| 13 | `services/ingestion-service/src/taxflow_ingestion/api.py` | Verify/Modify | Upload, idempotência e quarentena | @python-developer | 5, 11, 12 |
| 14 | `data/synthetic/pyproject.toml` | Verify/Modify | Pacote do gerador | @python-developer | None |
| 15 | `data/synthetic/src/generator.py` | Verify/Modify | Fixtures determinísticas | @test-generator | 3, 4, 14 |
| 16 | `tests/contract/test_data_contracts.py` | Verify/Modify | Compatibilidade e identidade | @data-quality-analyst | 3-5 |
| 17 | `tests/integration/test_ingestion_flow.py` | Verify/Modify | Fluxo válido/inválido/duplicado | @test-generator | 10-15 |
| 18 | `tests/security/test_tenant_isolation.py` | Verify/Modify | Política cross-tenant | @ecc-security-reviewer | 8, 9 |
| 19 | `.github/workflows/ci.yml` | Verify/Modify | Gate reproduzível | @ecc-code-architect | 1-18 |

**Total Files:** 19

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @ecc-code-architect / @ecc-architect | 1, 2, 5, 19 | Limites, contrato de API e CI |
| @pipeline-architect / @data-quality-analyst | 3, 4, 16 | Eventos, ODCS e gates de qualidade |
| @ecc-kotlin-build-resolver / @ecc-kotlin-reviewer | 7, 8 | Serviço Kotlin autocontido |
| @data-platform-security / @ecc-security-reviewer | 9, 18 | Isolamento em banco e testes negativos |
| @python-developer | 10-15 | Pydantic, parsing, FastAPI e fixtures |
| @test-generator | 15, 17 | Geração e integração determinísticas |
| (general) | 6 | Configuração simples |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: File type, purpose keywords, path patterns, KB domains

---

## Code Patterns

### Pattern 1: Envelope imutável

```python
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CanonicalTransaction(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: UUID
    tenant_id: UUID
    source_system: str = Field(min_length=1)
    source_event_id: str = Field(min_length=1)
    occurred_at: datetime
    operation_amount: Decimal = Field(ge=Decimal("0"), decimal_places=2)
```

### Pattern 2: Deny by default

```kotlin
fun authorize(contextTenantId: UUID, resourceTenantId: UUID, grantedRoles: Set<Role>, requiredRole: Role) {
    require(contextTenantId == resourceTenantId) { "cross-tenant access denied" }
    require(requiredRole in grantedRoles) { "required role not granted" }
}
```

### Pattern 3: Configuration Structure

```yaml
tenancy:
  require_tenant_context: true
  deny_cross_tenant_by_default: true
events:
  schema_compatibility: backward
  max_retries: 5
data:
  synthetic_profile: small
```

---

## Data Flow

```text
1. Gerador produz XML/CSV/XLSX determinístico
   |
   v
2. Ingestion resolve contexto autenticado do tenant
   |
   v
3. Parser converte registro para mapping
   |
   v
4. Pydantic valida envelope canônico
   |--- inválido ---> quarentena com motivo
   |--- duplicado --> contador sem segundo efeito
   `--- válido ----> evento aceito
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| CI runner | GitHub Actions | OIDC/GITHUB_TOKEN mínimo |
| Identity provider futuro | OIDC | Fora desta onda; contrato de contexto somente |
| ERP/banco futuro | Contract adapter | Fora desta onda; dados sintéticos |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Modelos, parsers, generator e RBAC | Service-local tests | pytest/JUnit | ≥90% no núcleo da Fundação |
| Contract | Avro, ODCS e OpenAPI | `tests/contract/` | pytest + parsers | 100% dos contratos |
| Integration | Ingestão CSV válida, inválida e duplicada | `tests/integration/` | pytest/FastAPI | Todos os caminhos da Fundação |
| Security | Negação cross-tenant e role ausente | `tests/security/` | pytest/JUnit | Zero bypass |
| Smoke | 100 mil registros sintéticos | Generator test | pytest | Completo em até 10 segundos local ou SLO CI registrado |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Formato não suportado | Retornar 422 com tipo permitido | No |
| Registro inválido | Quarentena com correlação e código | No |
| Evento duplicado | Retornar resultado idempotente | No effect |
| Tenant ausente/divergente | Negar e auditar | No |
| Dependência de parser ausente | Falhar startup/teste com mensagem explícita | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `tenancy.require_tenant_context` | bool | `true` | Impede operação anônima |
| `tenancy.deny_cross_tenant_by_default` | bool | `true` | Política padrão |
| `events.schema_compatibility` | enum | `backward` | Evolução de contratos |
| `events.max_retries` | int | `5` | Limite futuro de retry |
| `data.synthetic_profile` | enum | `small` | Perfil local da Fundação |

---

## Security Considerations

- Tenant não é confiado a partir do payload de negócio.
- Dados sintéticos não contêm PII real.
- Nenhuma credencial é versionada ou possui fallback local.
- Logs registram IDs de correlação sem payload fiscal integral.
- CI usa permissões mínimas e executa secret scan.
- Migração aplica isolamento no banco, além da autorização de aplicação.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | JSON com correlação, fonte e tenant pseudonimizado |
| Metrics | Aceitos, inválidos, duplicados e latência de parsing |
| Tracing | W3C Trace Context preparado no contrato HTTP |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Synthetic Files] → [Parse] → [Contract Gate] → [Accepted Events]
                                    |
                                    `----------→ [Quarantine]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| N/A in Foundation | N/A | N/A | Persistência analítica entra na Wave 2 |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| In-memory foundation acceptance | Idempotent by source identity | `tenant_id`, `source_system`, `source_event_id` | Current test run |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Optional field | Backward-compatible minor version | Revert consumer to previous schema |
| Required/breaking field | New major version | Keep previous major active |
| Removal | Deprecation window and consumer inventory | Restore previous schema |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Required identity | pytest/Avro | 100% | Block CI |
| Valid accepted record | Pydantic | 100% | Quarantine |
| Accounting completeness | pytest | Accepted + invalid + duplicate = received | Block CI |
| Tenant isolation | pytest/JUnit | Zero bypass | Block CI |
| Secret scan | gitleaks | Zero finding | Block CI |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-14 | iterate-agent | Created Wave 1 Foundation design from master design v1.1 |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_FOUNDATION_TAXFLOW_360.md`
