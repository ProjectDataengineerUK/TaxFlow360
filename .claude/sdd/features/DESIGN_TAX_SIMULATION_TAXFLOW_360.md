# DESIGN: Simulador Tributário TaxFlow 360

> Technical design for deterministic current-regime, CBS/IBS and split-payment simulations with mandatory official-source links

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | TAX_SIMULATION_TAXFLOW_360 |
| **Date** | 2026-08-15 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_TAX_SIMULATION_TAXFLOW_360.md](./DEFINE_TAX_SIMULATION_TAXFLOW_360.md) |
| **Parent DESIGN** | [DESIGN_PLATAFORMA_TAXFLOW_360.md](./DESIGN_PLATAFORMA_TAXFLOW_360.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
Canonical operation + tenant/CNPJ + effective_at + idempotency_key
                              |
                              v
                 [Authorization / Eligibility]
                              |
                              v
       [Approved Rule Catalog + immutable official sources]
          | current       | transition       | split
          v               v                  v
     [Tax Engine]    [Tax Engine]     [Payment Allocator]
          |               |                  |
          +---------------+------------------+
                              |
                    [Scenario Comparator]
                              |
         +--------------------+--------------------+
         |                    |                    |
         v                    v                    v
 [Calculation Memory] [Official Source Links] [Immutable Result]
         |                                         |
         +--------------------+--------------------+
                              |
                 [Query API / Control Tower]

Batch path: Silver operations -> Databricks simulator -> Gold results
Parity oracle: same golden inputs + rule snapshot -> identical monetary outputs
Future Wave 6: official documents -> vector index -> proposals only -> human approval
```

The cloud-neutral Kotlin core owns synchronous rule selection and monetary calculation. PostgreSQL owns approved rule versions and immutable simulation metadata. Databricks applies the same rule snapshot to accepted Silver operations for batch simulation. Every official result contains a non-empty list of source references; the API and UI render those references as clickable links.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Simulation Contract | Stable request/result, memory and source-reference schema | OpenAPI + ODCS YAML |
| Official Source Reference | URL, authority, document, provision, publication/capture time and content hash | Kotlin value object + PostgreSQL/Delta struct |
| Rule Catalog | Append-only versioned rules, effective intervals and four-eyes state | Kotlin + PostgreSQL |
| Rule Selector | Select exactly one approved version for operation facts and logical time | Kotlin, deterministic predicates |
| Tax Calculator | Calculate current/CBS/IBS components with decimal arithmetic | Kotlin `BigDecimal`, HALF_EVEN |
| Split Allocator | Allocate authority/company values across installments and reversals | Kotlin `BigDecimal` |
| Scenario Comparator | Produce component-level deltas between current, transition and split | Kotlin |
| Simulation Repository | Idempotent immutable result and outbox persistence | PostgreSQL transaction |
| Query API | Tenant-scoped latest/result/comparison endpoints | FastAPI |
| Batch Simulator | Apply frozen rule snapshots to 100k accepted operations | Databricks, PySpark, Delta |
| Control Tower | Display scenarios, deltas, memory and clickable official sources | Next.js, TypeScript |
| Golden/Parity Suite | Validate 50+ cases, boundaries, split invariants and engine parity | JUnit + pytest |

---

## Key Decisions

### Decision 1: Structured approved catalog is the calculation authority

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-15 |

**Context:** Legislation is textual, temporal and subject to interpretation, while a financial calculation must be deterministic, low-latency and reproducible.

**Choice:** Convert validated legal interpretation into immutable structured rule versions. Only `APPROVED` rules with a matching effective interval and at least one validated official source can participate in an official calculation.

**Rationale:** It separates legal research from runtime computation. A calculation can be reproduced from facts plus a rule snapshot without network access or probabilistic retrieval.

**Alternatives Rejected:**
1. Query legislation or RAG during calculation - rejected because retrieval is probabilistic, slow and not a safe monetary authority.
2. Hardcode rates in application code - rejected because temporal changes would require deployment and obscure approval/audit history.
3. Call an external calculator as the only runtime engine - rejected because availability and version drift would prevent deterministic replay.

**Consequences:**
- Tax specialists must approve and publish rule records before official use.
- Vector retrieval in Wave 6 may propose evidence, but cannot publish or calculate.
- The official calculator can act as a parity oracle, not an unversioned runtime dependency.

---

### Decision 2: Official citations are mandatory domain data

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-15 |

**Context:** A plain `legalBasis` string does not allow a user or auditor to verify the origin of a rate.

**Choice:** Model `LegalSource` as a required immutable value object containing `source_url`, authority, document identifier, provision, publication date, capture timestamp, SHA-256 content hash and source status. Publication fails if a rule has no source or uses a URL outside the governed authority allowlist.

**Rationale:** Citations become enforceable by schema, tests and publication rules instead of presentation convention.

**Alternatives Rejected:**
1. Add links only in frontend text - rejected because other consumers could omit them.
2. Store only a URL - rejected because content can change and a URL alone cannot reproduce the reviewed source.

**Consequences:**
- Every tax API response includes clickable official sources.
- Captured documents remain a future Wave 6 artifact; Wave 3 stores metadata/hash and approved links.

---

### Decision 3: One semantic calculation contract, two execution engines

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-15 |

**Context:** Interactive requests need low latency while historical simulation needs distributed processing.

**Choice:** Kotlin remains the transactional reference implementation. Databricks consumes an immutable exported rule snapshot and must pass the same golden vectors, decimal scale, rounding and residual-allocation rules.

**Rationale:** Keeps the core cloud-neutral while using Spark for batch scale.

**Alternatives Rejected:**
1. Put all calculations in Databricks - rejected due to interactive latency and coupling.
2. Maintain unrelated Kotlin and PySpark formulas - rejected because semantic drift would be inevitable.

**Consequences:**
- CI blocks releases on parity mismatch.
- No shared runtime library crosses deployable units; the versioned contract and golden cases are the boundary.

---

### Decision 4: Append-only results and deterministic idempotency

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-15 |

**Context:** Recalculation under a new rule must not rewrite the result previously shown to a user.

**Choice:** Fingerprint tenant, operation, scenario set, cutoff and rule-set version. Repeat requests return the existing result. Any changed input creates a new simulation linked to its predecessor.

**Rationale:** Provides retry safety and full audit history.

**Alternatives Rejected:**
1. Update the existing result - rejected because it destroys evidence.
2. Idempotency by operation ID only - rejected because legitimate new scenarios and rule versions would collide.

**Consequences:**
- Storage grows append-only and needs retention/partition management.
- Corrections are explicit invalidation/supersession events.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `contracts/data/tax-simulation.contract.yaml` | Create | ODCS result, memory, citation and lineage contract | @data-contracts-engineer | None |
| 2 | `contracts/api/openapi.yaml` | Modify | Simulation, comparison and source-reference API schemas | (general) | 1 |
| 3 | `config/official-source-authorities.yaml` | Create | Governed authority/domain allowlist | @especialista-tributario | None |
| 4 | `config/tax-rule-catalog.yaml` | Create | Synthetic approved current/CBS/IBS rule snapshot | @especialista-tributario | 3 |
| 5 | `services/tax-service/src/main/kotlin/taxflow/tax/domain/LegalSource.kt` | Create | Mandatory validated official citation value object | @ecc-kotlin-reviewer | 3 |
| 6 | `services/tax-service/src/main/kotlin/taxflow/tax/domain/TaxRule.kt` | Modify | Structured predicates, sources and four-eyes publication | @ecc-kotlin-reviewer | 5 |
| 7 | `services/tax-service/src/main/kotlin/taxflow/tax/domain/TaxCalculator.kt` | Modify | Multi-component calculation and complete memory | @ecc-kotlin-reviewer | 6 |
| 8 | `services/tax-service/src/main/kotlin/taxflow/tax/domain/Simulation.kt` | Create | Scenario comparison, fingerprint and immutable result | @ecc-kotlin-reviewer | 6, 7 |
| 9 | `services/tax-service/src/main/kotlin/taxflow/tax/Application.kt` | Modify | Tenant-scoped publish/calculate/query endpoints | @ecc-kotlin-reviewer | 8 |
| 10 | `services/tax-service/src/main/resources/db/migration/V2__simulation.sql` | Create | Rule/source/result/outbox tables and RLS | @data-platform-security | 1, 8 |
| 11 | `services/payment-service/src/main/kotlin/taxflow/payment/Application.kt` | Modify | Installment, reversal and refund split allocation | @ecc-kotlin-reviewer | 1 |
| 12 | `services/query-service/src/taxflow_query/api.py` | Modify | Tenant-scoped simulation reads/comparison | @python-developer | 1, 2 |
| 13 | `data/databricks/resources/simulator.yml` | Create | Batch job/pipeline configuration | @databricks-spark-expert | 1, 4 |
| 14 | `data/databricks/src/tax_rule_catalog.py` | Create | Strict rule/source snapshot loader | @databricks-spark-expert | 3, 4 |
| 15 | `data/databricks/src/gold_simulator.py` | Modify | Equivalent scenario calculation and immutable Gold output | @databricks-spark-expert | 13, 14 |
| 16 | `apps/control-tower/src/app/simulator/page.tsx` | Create | Scenario comparison, memory and clickable citations | @ecc-typescript-reviewer | 2 |
| 17 | `services/tax-service/src/test/kotlin/taxflow/tax/domain/TaxCalculatorTest.kt` | Modify | Rule, citation, formula and boundary tests | @test-generator | 5-8 |
| 18 | `services/payment-service/src/test/kotlin/taxflow/payment/PaymentEngineTest.kt` | Modify | Split sum, installment, residual and reversal invariants | @test-generator | 11 |
| 19 | `tests/golden/tax-simulation-cases.yaml` | Create | At least 50 versioned synthetic golden cases | @especialista-tributario | 1, 4 |
| 20 | `tests/golden/test_tax_cases.py` | Modify | Golden contract and expected-result checks | @test-generator | 14, 19 |
| 21 | `tests/parity/test_tax_simulation_parity.py` | Create | Kotlin-contract/PySpark semantic parity oracle | @test-generator | 7, 15, 19 |
| 22 | `tests/security/test_official_source_links.py` | Create | Missing/non-official/cross-tenant source rejection | @ecc-security-reviewer | 2, 3, 9 |
| 23 | `tests/performance/test_tax_simulation_load.py` | Create | 100k batch and reference-engine performance gate | @test-generator | 15, 19 |
| 24 | `.github/workflows/ci.yml` | Modify | JVM, golden, citation, parity and batch gates | @ci-cd-specialist | 17-23 |

**Total Files:** 24

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @data-contracts-engineer | 1 | ODCS schema, provenance and compatibility |
| @especialista-tributario | 3, 4, 19 | Legal authority, rules and golden outcomes require domain review |
| @ecc-kotlin-reviewer | 5-9, 11 | Kotlin domain invariants, decimal arithmetic and transactional API |
| @data-platform-security | 10 | PostgreSQL RLS, immutable audit and outbox safety |
| @python-developer | 12 | FastAPI tenant-scoped query integration |
| @databricks-spark-expert | 13-15 | Delta/Spark batch implementation and performance |
| @ecc-typescript-reviewer | 16 | Next.js type safety and accessible citation rendering |
| @test-generator | 17, 18, 20, 21, 23 | Boundary, property, golden, parity and load tests |
| @ecc-security-reviewer | 22 | URL allowlist, SSRF avoidance and tenant-negative testing |
| @ci-cd-specialist | 24 | Hosted multi-runtime quality gates |
| (general) | 2 | No dedicated API designer was discovered; Build follows the existing OpenAPI conventions |

**Agent Discovery:**
- Scanned: `${CLAUDE_PLUGIN_ROOT}/agents/**/*.md`
- Matched by: Kotlin/API/tax/Spark/contract/security/testing keywords and target paths
- Confidence: 0.95 (KB patterns and specialist matches found)

---

## Code Patterns

### Pattern 1: Required immutable official source

```kotlin
data class LegalSource(
    val sourceUrl: URI,
    val authority: String,
    val documentId: String,
    val provision: String,
    val publishedOn: LocalDate,
    val capturedAt: Instant,
    val contentSha256: String,
) {
    init {
        require(sourceUrl.scheme == "https")
        require(authority.isNotBlank() && documentId.isNotBlank() && provision.isNotBlank())
        require(Regex("^[a-f0-9]{64}$").matches(contentSha256))
    }
}
```

The publication service additionally checks the normalized hostname against `official-source-authorities.yaml`; it never fetches the URL during a calculation.

### Pattern 2: Temporal selection without implicit current time

```kotlin
fun selectRule(rules: List<TaxRule>, facts: OperationFacts): TaxRule =
    rules.asSequence()
        .filter { it.status == RuleStatus.APPROVED }
        .filter { it.validFrom <= facts.effectiveAt }
        .filter { it.validUntil == null || facts.effectiveAt < it.validUntil }
        .filter { it.matches(facts) }
        .sortedWith(compareByDescending<TaxRule> { it.priority }.thenByDescending { it.validFrom })
        .singleOrNull()
        ?: throw RuleResolutionException("exactly one approved effective rule is required")
```

Overlapping rules with the same precedence are a publication error, not a runtime tie-break.

### Pattern 3: Deterministic split residual

```kotlin
fun allocate(total: BigDecimal, weights: List<BigDecimal>): List<BigDecimal> {
    require(weights.isNotEmpty() && weights.all { it >= BigDecimal.ZERO })
    val denominator = weights.sumOf { it }
    require(denominator > BigDecimal.ZERO)
    val allocated = weights.map {
        total.multiply(it).divide(denominator, 2, RoundingMode.HALF_EVEN)
    }.toMutableList()
    allocated[allocated.lastIndex] = allocated.last().add(total.subtract(allocated.sumOf { it }))
    check(allocated.sumOf { it } == total)
    return allocated
}
```

### Pattern 4: Configuration structure

```yaml
catalog:
  version: 1.0.0
  status: synthetic-approved
  rounding:
    scale: 2
    mode: HALF_EVEN
  rules:
    - id: cbs-general-2026
      tax: CBS
      rate: "0.009"
      valid_from: 2026-01-01T00:00:00Z
      valid_until: 2027-01-01T00:00:00Z
      status: approved
      author_id: tax-specialist-a
      approver_id: tax-specialist-b
      sources:
        - source_url: https://www.gov.br/receitafederal/example
          authority: Receita Federal do Brasil
          document_id: synthetic-reference
          provision: synthetic-test-case
          content_sha256: 64-lowercase-hex-characters
```

Build data remains explicitly synthetic until specialists replace and approve the catalog entries.

---

## Data Flow

```text
1. User submits canonical operation, scenario set and idempotency key
   |
   v
2. API authenticates tenant/CNPJ and validates eligibility
   |
   v
3. Rule selector resolves one approved effective rule per component
   |
   v
4. Tax Engine calculates current, transition and CBS/IBS components
   |
   v
5. Payment Engine allocates simulated split/installments/reversals
   |
   v
6. Comparator produces deltas and complete calculation memory
   |
   v
7. Repository atomically writes result + sources + audit + outbox
   |
   v
8. API/UI returns values with clickable official-source links
```

No step performs live legal-document retrieval. Wave 6 ingestion produces proposals that enter the same approval workflow before a future rule catalog version is published.

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Official government sources | Approved HTTPS links and captured metadata; no runtime fetch | Public source + governance review |
| Official tax calculator | Offline/versioned parity fixture when made available | Version-specific distribution/API credential if required |
| PostgreSQL | Transactional rules/results/outbox | Workload identity + TLS |
| Databricks/Unity Catalog | Rule snapshot and Gold batch output | Cloud workload identity |
| Control Tower | Tax/query REST APIs | OIDC/JWT tenant claims |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Rule selection, decimal formulas, memory, fingerprint | 17 | JUnit 5 | 100% operators/boundaries |
| Property | Split, installments, reversals and residual cents | 18 | JUnit parameterized/property cases | Sum invariant for all generated cases |
| Contract | ODCS/OpenAPI/catalog/source metadata | 20, 22 | pytest + PyYAML | 100% required fields |
| Golden | 50+ specialist-approved synthetic cases | 19, 20 | pytest/JUnit | 100% exact expected values |
| Parity | Reference versus batch semantics | 21 | pytest + Decimal/PySpark | 100% money/rule/source IDs |
| Security | Missing source, host confusion, cross-tenant access | 22 | pytest/API tests | 100% negative cases blocked |
| Performance | Unit p95 and 100k batch | 23 | pytest + controlled CI/Databricks | p95 <=500 ms; batch <=15 min |
| E2E | Request through query/UI response | CI + hosted environment | API/browser checks | TS-AT-001 through TS-AT-014 |

Acceptance coverage:

| Acceptance Tests | Primary Evidence |
|------------------|------------------|
| TS-AT-001, 002, 003, 008, 011 | 17, 19, 20 |
| TS-AT-004, 005, 006 | 18 |
| TS-AT-007 | 8, 9, integration assertions |
| TS-AT-009 | 10, 22 |
| TS-AT-010 | 21 |
| TS-AT-012 | 17, 20 |
| TS-AT-013, 014 | 5, 16, 22 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| No approved/effective rule | 422 with structured missing-rule reason; no official result | No |
| Ambiguous overlapping rules | Block catalog publication and raise governance incident | No |
| Missing/invalid official source | Block rule publication; never calculate officially | No |
| Unauthorized tenant/CNPJ | 404/deny without resource disclosure; audit attempt | No |
| Duplicate idempotency key/same fingerprint | Return existing immutable result | Safe return |
| Duplicate key/different fingerprint | 409 conflict | No |
| Transient database/outbox failure | Roll back atomically and retry with backoff | Yes |
| Batch record invalid | Quarantine with reason and lineage | After correction |
| Parity mismatch | Block release/catalog promotion | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `tax.catalog.version` | semver | none | Required frozen rule snapshot |
| `tax.rounding.scale` | integer | `2` | Monetary output scale |
| `tax.rounding.mode` | enum | `HALF_EVEN` | Shared rounding contract |
| `tax.sources.allowed_authorities` | list | governed file | Authority/domain allowlist |
| `tax.sources.require_https` | boolean | `true` | Reject non-HTTPS official links |
| `tax.sources.require_sha256` | boolean | `true` | Require reviewed content fingerprint |
| `tax.simulation.max_scenarios` | integer | `3` | Bound synchronous requests |
| `tax.batch.max_concurrent_runs` | integer | `1` | Prevent overlapping snapshot publication |

---

## Security Considerations

- Apply tenant/CNPJ authorization before rule lookup, calculation and result lookup.
- Use PostgreSQL RLS and `FORCE ROW LEVEL SECURITY` for tenant-scoped tables.
- Do not fetch user-provided URLs; official-source URLs are reviewed metadata, preventing SSRF.
- Normalize hostnames, require HTTPS and reject credentials, IP literals, redirects and deceptive suffixes during publication validation.
- Treat source documents and hashes as immutable audit evidence.
- Ensure author and approver differ; record both identities and timestamps.
- Never log complete operation payloads, tax IDs or authorization tokens.
- Vector retrieval in Wave 6 is read/proposal-only and cannot call rule-publication endpoints without human approval.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured correlation with tenant token, simulation ID, rule-set version and source IDs; no sensitive payload |
| Metrics | Latency, rule-resolution failures, missing-source blocks, idempotency hits, parity mismatch and batch SLA |
| Tracing | OpenTelemetry spans across API, Tax Engine, Payment Engine, repository and outbox |
| Audit | Append-only events for proposal, approval, publication, calculation, query, supersession and denial |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Accepted Silver Operations] -------+
                                     v
[Approved Rule Snapshot] -> [Validate Snapshot] -> [Resolve Temporal Rules]
                                     |                       |
                                     v                       v
                              [Quality Block]        [Calculate Scenarios]
                                                             |
                                                             v
                                                    [Parity/Invariant Gate]
                                                       |             |
                                                     fail          pass
                                                       v             v
                                                [Quarantine] [Gold Simulation]
                                                                     |
                                                                     v
                                                              [Query/UI]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|-------------|-------------|-----------|
| `gold_tax_simulation` | `tenant_id`, `effective_date` | tenant/day with liquid clustering by CNPJ | Tenant pruning and temporal queries |
| `gold_tax_simulation_component` | `simulation_id` clustering | logical parent grouping | Fast memory reconstruction |
| `gold_tax_simulation_source` | `rule_set_version` clustering | catalog version | Citation audit and impact analysis |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Accepted operations | append/idempotent fingerprint | `operation_id`, `input_hash` | Closed batch only |
| Rule snapshot | immutable version load | `rule_set_version` | None; never mutate |
| Simulation result | insert-only | `simulation_fingerprint` | Retry current batch |
| Query latest | derived view/window | `published_at` | Current affected CNPJ |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Add optional component/source field | Additive contract minor version and nullable backfill | Consumer ignores field |
| Add required rule predicate | New catalog/contract version; dual validation window | Reuse previous approved snapshot |
| Decimal scale change | New major contract and parallel output columns | Continue prior version |
| Rename/remove field | Deprecate for at least one release; compatibility view | Restore alias/view |
| Change formula or rate | New immutable rule-set version, never table overwrite | Re-run using prior snapshot |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Identity/completeness | Spark expectations + contract tests | 0 missing tenant/CNPJ/operation/scenario | Block/quarantine |
| Rule resolution | Kotlin/Spark checks | Exactly 1 approved effective rule per component | Block publication |
| Official sources | Contract/allowlist check | >=1 valid source per applied rule | Block publication |
| Monetary bounds | Decimal invariant checks | No invalid negative/overflow values | Block/quarantine |
| Split preservation | Property/Spark aggregate | Exact sum at configured scale | Block release/batch |
| Golden parity | CI comparison | 100% values, rule IDs and source IDs | Block release |
| Freshness | Job metric | 100k <=15 minutes | Alert and block wave acceptance |
| Tenant isolation | RLS/API negative tests | 0 cross-tenant disclosures | Block release/security incident |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-15 | design-agent | Initial Wave 3 design with mandatory official-source citations and future vector boundary |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_TAX_SIMULATION_TAXFLOW_360.md`
