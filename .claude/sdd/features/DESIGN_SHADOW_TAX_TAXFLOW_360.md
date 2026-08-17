# DESIGN: Shadow Tax e Conciliação TaxFlow 360

> Technical design for implementing Shadow Tax e Conciliação TaxFlow 360

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | SHADOW_TAX_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_SHADOW_TAX_TAXFLOW_360.md](./DEFINE_SHADOW_TAX_TAXFLOW_360.md) |
| **Status** | Ready for Build |
| **Design Confidence** | 0.95 — KB patterns and specialist agents found |

---

## Architecture Overview

```text
[Fiscal CDF] [ERP CDF] [Payment CDF] [Split CDF] [Tax simulations]
      \          |          |           /              /
       +----> [Canonical event ledger + deduplication] <+
                         |
                  [Event-time correlation]
                  watermark + checkpoint
                         |
            [Four-way match + Shadow Tax]
              policy/version + Decimal
                  /             \
       [MATCH/version]      [DIVERGENCE/version]
              \                  |
               +------> [Delta Gold append-only]
                                |
                    [Transactional review inbox]
                    RBAC + immutable decisions
                                |
                 [Tenant-scoped Query API + UI]
```

The analytic pipeline owns deterministic correlation and classification. The reconciliation service owns human workflow and authorization. They communicate through versioned contracts and append-only records; neither deployable unit imports code from the other.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Event contract and policy | Canonical envelope, tolerance, materiality, windows and review rules | Avro/YAML/ODCS |
| Canonical event ledger | Validate, deduplicate and retain every source event and disposition | Spark Structured Streaming, Delta CDF |
| Correlation state | Assemble fiscal, ERP, payment and split by tenant/CNPJ/transaction using event time | Spark stateful streaming, checkpoint |
| Shadow comparator | Compare current and reform calculations and preserve legal provenance | Python, PySpark, Decimal |
| Reconciliation engine | Deterministic four-way match and divergence classification | Kotlin/Spring |
| Review workflow | Assignment and guarded state transitions for human decisions | Kotlin/Spring, PostgreSQL RLS/outbox |
| Gold models | Immutable reconciliation, divergence, late-event and metric history | Delta Lake |
| Query API | Tenant-scoped latest/history/detail/metrics/review reads | FastAPI/Pydantic |
| Control Tower | Accessible operational queue and evidence drill-down | Next.js/TypeScript |

---

## Key Decisions

### Decision 1: Event-time state with governed watermark

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Four independent sources can arrive out of order, be duplicated or arrive after an initial result. Processing-time joins would make replay nondeterministic and could silently change closed cases.

**Choice:** Correlate on `(tenant_id, company_tax_id, tax_transaction_id)` using source event time, a policy-defined 24-hour initial watermark, durable checkpoints and an explicit logical cutoff. Events beyond retention enter an append-only late-event stream and require controlled replay or human disposition.

**Rationale:** Event time preserves semantic ordering, while watermark bounds state and makes missing-source detection measurable. Explicit late-event handling prevents silent loss. A recorded cutoff, policy checksum and input IDs make results reproducible after checkpoint restoration.

**Alternatives Rejected:**
1. Unbounded state — rejected because state growth and recovery time are operationally unsafe.
2. Processing-time timeout — rejected because identical input logs could produce different outcomes.
3. Silently discard late events — rejected because it violates completeness and audit requirements.

**Consequences:**
- A too-short window can create provisional missing-source cases; policy approval and late-event metrics mitigate this.
- Replay is deterministic and every event receives an auditable disposition.

---

### Decision 2: At-least-once transport with exactly-once domain effect

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** External transports and checkpoint recovery can redeliver data.

**Choice:** Deduplicate by `(tenant, source, event_id, event_version)` and fingerprint each reconciliation from sorted input IDs, policy version and cutoff. Inserts are idempotent; a reused idempotency key with different content is rejected.

**Rationale:** This provides the required semantic guarantee without making an unverifiable transport-level exactly-once claim.

**Alternatives Rejected:**
1. Trust broker delivery semantics — rejected because downstream retries still duplicate effects.
2. Mutable upsert only — rejected because it removes historical evidence.

**Consequences:**
- Duplicate events remain counted in the audit ledger but do not duplicate business effects.
- Stable canonical serialization becomes a contract requirement.

---

### Decision 3: Append-only version history and derived latest views

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Late data, reversals and reviews may change the current interpretation without erasing the prior decision.

**Choice:** Persist new reconciliation, divergence and review versions; expose latest state through deterministic views. No business history is updated in place.

**Rationale:** Append-only records support replay comparison, temporal audit and safe invalidation.

**Alternatives Rejected:**
1. Overwrite current rows — rejected because it destroys evidence.
2. Event sourcing without materialized views — rejected because operational queries would be unnecessarily expensive.

**Consequences:**
- Storage grows with changes; retention and compaction are operational concerns.
- Queries must explicitly select the latest authorized version.

---

### Decision 4: Versioned policy and mandatory human gate

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Tolerances, materiality and review roles are governance decisions, not constants.

**Choice:** Load approved YAML policy with checksum and effective dates. `CRITICAL` and ambiguous cases transition only to `PENDING_HUMAN_REVIEW`; closure requires an authorized actor, justification and evidence.

**Rationale:** Configuration preserves reproducibility and four-eyes governance while preventing automated fiscal correction.

**Alternatives Rejected:**
1. Hard-coded thresholds — rejected because historic outcomes could not identify their governing policy.
2. Automatic critical closure — rejected because it violates the stated audit boundary.

**Consequences:**
- Draft/unapproved policies can run only as non-publishable synthetic evaluations.
- Review latency is observable and governed by SLA.

---

### Decision 5: Reuse Wave 3 legal provenance

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Shadow Tax must explain tax differences without creating a competing legal catalog.

**Choice:** Tax divergences require simulation, rule, calculation-memory and official-source IDs inherited from the immutable Wave 3 artifacts. No live legal fetch occurs in this wave.

**Rationale:** One governed source chain prevents contradictory rates and ensures every displayed link resolves to the calculation evidence.

**Alternatives Rejected:**
1. Copy legislation into reconciliation — rejected due to provenance drift.
2. Fetch live pages during streaming — rejected due to nondeterminism and availability/security risk.

**Consequences:**
- Missing provenance blocks publication of a tax divergence.
- Regulatory ingestion and vector search remain Wave 6 scope.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `contracts/data/shadow-tax-divergence.contract.yaml` | Create | ODCS reconciliation/divergence contract | @data-contracts-engineer | None |
| 2 | `contracts/events/reconciliation-event.avsc` | Create | Canonical versioned event envelope | @data-contracts-engineer | None |
| 3 | `config/reconciliation-policy.yaml` | Create | Windows, tolerances, severity, workflow and approvals | @data-governance-auditor | None |
| 4 | `services/reconciliation-service/src/main/kotlin/taxflow/reconciliation/domain/Reconciliation.kt` | Create | Domain types and state machine | @ecc-kotlin-reviewer | 1, 3 |
| 5 | `services/reconciliation-service/src/main/kotlin/taxflow/reconciliation/domain/ReconciliationEngine.kt` | Create | Four-way matcher, Decimal policy and fingerprints | @ecc-kotlin-reviewer | 4 |
| 6 | `services/reconciliation-service/src/main/kotlin/taxflow/reconciliation/Application.kt` | Modify | Tenant-scoped reconcile/review endpoints and outbox | @ecc-kotlin-reviewer | 4, 5 |
| 7 | `services/reconciliation-service/src/main/resources/db/migration/V1__reconciliation.sql` | Create | Append-only state, review, outbox and forced RLS | @data-platform-security | 1, 4 |
| 8 | `services/reconciliation-service/src/test/kotlin/taxflow/reconciliation/ReconciliationTest.kt` | Modify | Domain, idempotency, workflow and isolation tests | @test-generator | 4-7 |
| 9 | `data/databricks/resources/shadow_tax.yml` | Create | Lakeflow streaming jobs, checkpoints and alerts | @lakeflow-architect | 1-3 |
| 10 | `data/databricks/src/reconciliation_policy.py` | Create | Strict approved-policy loader/checksum | @python-developer | 3 |
| 11 | `data/databricks/src/shadow_tax_reference.py` | Create | Runtime-neutral deterministic reference engine | @python-developer | 1, 10 |
| 12 | `data/databricks/src/gold_shadow_tax.py` | Modify | Stateful four-source correlation and Gold history | @spark-streaming-architect | 1, 2, 9-11 |
| 13 | `data/databricks/src/shadow_tax_metrics.py` | Create | Reconciliation, materiality, aging and SLA marts | @databricks-spark-expert | 12 |
| 14 | `services/query-service/src/taxflow_query/shadow_tax.py` | Create | API models and authorization-safe projections | @python-developer | 1 |
| 15 | `services/query-service/src/taxflow_query/shadow_tax_repository.py` | Create | Tenant/CNPJ latest, history, metrics and detail queries | @python-developer | 14 |
| 16 | `services/query-service/src/taxflow_query/api.py` | Modify | Shadow Tax query routes without regressing prior waves | @python-developer | 14, 15 |
| 17 | `contracts/api/openapi.yaml` | Modify | Query and review route contracts | @data-contracts-engineer | 1, 6, 16 |
| 18 | `apps/control-tower/src/app/shadow-tax/page.tsx` | Create | Accessible queue, filters, evidence and official links | @ecc-typescript-reviewer | 17 |
| 19 | `tests/golden/shadow-tax-cases.yaml` | Create | Deterministic match/divergence/reversal fixtures | @test-generator | 1-3 |
| 20 | `tests/golden/test_shadow_tax_cases.py` | Create | Reference/runtime parity and all divergence types | @test-generator | 11, 19 |
| 21 | `tests/streaming/test_shadow_tax_replay.py` | Create | Duplicate, late, checkpoint and replay semantics | @spark-streaming-architect | 9-12, 19 |
| 22 | `tests/security/test_shadow_tax_isolation.py` | Create | RLS, non-disclosure, roles and official-link lineage | @ecc-security-reviewer | 6, 7, 16, 17 |
| 23 | `tests/performance/test_shadow_tax_100k.py` | Create | 100k completeness and freshness gate | @ecc-performance-optimizer | 11-13, 19 |
| 24 | `.github/workflows/shadow-tax.yml` | Create | Static, unit, contract, parity, security and hosted gates | @ci-cd-specialist | 1-23 |

**Total Files:** 24

---

## Agent Assignment Rationale

> Agents discovered from `.claude/agents/`; Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @data-contracts-engineer | 1, 2, 17 | ODCS, Avro and API compatibility |
| @data-governance-auditor | 3 | Governed policy and approval semantics |
| @ecc-kotlin-reviewer | 4-6 | Kotlin domain modeling and Spring boundary |
| @data-platform-security | 7 | PostgreSQL RLS and immutable audit storage |
| @test-generator | 8, 19, 20 | Acceptance fixtures and deterministic tests |
| @lakeflow-architect | 9 | Lakeflow deployment and checkpoints |
| @python-developer | 10, 11, 14-16 | Decimal reference logic and FastAPI conventions |
| @spark-streaming-architect | 12, 21 | Watermark, state, deduplication and replay |
| @databricks-spark-expert | 13 | Delta analytical metrics |
| @ecc-typescript-reviewer | 18 | Accessible typed frontend |
| @ecc-security-reviewer | 22 | Tenant/RBAC/adversarial verification |
| @ecc-performance-optimizer | 23 | Scale and latency evidence |
| @ci-cd-specialist | 24 | Hosted multi-runtime gates |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: file type, purpose, path and DEFINE KB domains

---

## Code Patterns

### Pattern 1: Decimal classification from versioned policy

```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

@dataclass(frozen=True)
class MatchResult:
    status: str
    difference: Decimal

def compare(expected: Decimal, actual: Decimal, tolerance: Decimal) -> MatchResult:
    difference = abs(expected - actual).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    if difference == Decimal("0.00"):
        status = "MATCHED"
    elif difference <= tolerance:
        status = "MATCHED_WITH_TOLERANCE"
    else:
        status = "AMOUNT_MISMATCH"
    return MatchResult(
        status=status,
        difference=difference,
    )
```

### Pattern 2: Stable semantic fingerprint

```python
import hashlib
import json

def fingerprint(*, tenant_id: str, source_ids: list[str], policy_checksum: str,
                logical_cutoff: str) -> str:
    body = {
        "tenantId": tenant_id,
        "sourceIds": sorted(source_ids),
        "policyChecksum": policy_checksum,
        "logicalCutoff": logical_cutoff,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()
```

### Pattern 3: Configuration Structure

```yaml
version: 1.0.0
status: approved
effectiveFrom: "2026-08-17T00:00:00Z"
watermark: PT24H
tolerances:
  - divergenceType: amount
    currency: BRL
    paymentMethod: any
    absolute: "0.01"
materiality:
  review: "100.00"
  high: "1000.00"
  critical: "10000.00"
workflow:
  criticalRequiresHumanReview: true
  autoCloseCritical: false
approval:
  preparedBy: synthetic-policy-author
  approvedBy: synthetic-policy-reviewer
```

### Pattern 4: Stateful stream boundary

```python
events = (
    spark.readStream.option("readChangeFeed", "true").table("silver_canonical_events")
    .withWatermark("event_time", policy.watermark)
    .dropDuplicatesWithinWatermark(["tenant_id", "source", "event_id", "event_version"])
)

# Correlation logic receives only canonical, tenant-qualified events and emits
# immutable result versions. Checkpoint location is unique per target table.
```

---

## Data Flow

```text
1. Source CDF/event is validated against the canonical envelope.
   |
2. Ledger records accepted, duplicate, invalid or too-late disposition.
   |
3. Event-time state assembles four points by tenant/CNPJ/transaction.
   |
4. Last point or watermark triggers four-way and current/reform comparison.
   |
5. Policy classifies status, divergence, severity and materiality.
   |
6. A new immutable version and provenance are committed to Gold.
   |
7. Critical/ambiguous cases enter the transactional human-review inbox.
   |
8. Authorized APIs expose latest/history/metrics and official evidence links.
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Fiscal/ERP/payment/split synthetic sources | Delta CDF/canonical event | Workload identity + tenant claims |
| Wave 3 Tax Simulation | Append-only Delta/IDs | Internal service identity; read-only |
| PostgreSQL review store | JDBC/Spring transaction + outbox | Managed secret/workload identity; forced RLS |
| Databricks | Lakeflow/Delta/checkpoint volume | Cloud workload identity |
| AWS/Azure/GCP storage | Encrypted object storage | Least-privilege cloud identity |
| Official legal sources | Stored HTTPS references only | No runtime fetch; allowlisted provenance |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Match, tolerance, severity, fingerprints, workflow | 8, 20 | JUnit, pytest | ST-AT-001,003-005,009,010,015 |
| Contract | ODCS/Avro/OpenAPI/policy invariants | 1-3, 17 | YAML/Avro/OpenAPI validators | Required fields and compatibility |
| Streaming integration | Missing, duplicate, late, checkpoint and replay | 21 | Spark local/Databricks hosted | ST-AT-002,006-008,013 |
| API/security | Query, review RBAC, tenant non-disclosure | 8, 22 | JUnit, pytest/FastAPI | ST-AT-010-012 |
| Golden/parity | All divergence types and legal provenance | 19, 20 | pytest | 100% inserted divergences; ST-AT-004 |
| Performance | 100k four-point transactions, completeness, p95 | 23 | Databricks hosted metrics | ST-AT-014 and freshness SLO |
| E2E | Event through review decision and history | 8, 21, 22 | Hosted CI | All acceptance tests; no critical false match |

No Ship claim is allowed until JVM, frontend and Databricks hosted gates run in their real runtimes.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid schema/tenant/currency | Quarantine with reason and source hash; never correlate | No, until corrected version |
| Duplicate event | Audit duplicate disposition; suppress domain effect | Safe redelivery |
| Event inside late window | Emit a new result version preserving prior state | Automatic |
| Event beyond retention | Late-event table and controlled replay/review | Manual/controlled |
| Ambiguous correlation | `PENDING_HUMAN_REVIEW`; no fuzzy silent match | No automatic |
| Missing tax provenance | Block tax-divergence publication and alert quality gate | After dependency repair |
| Checkpoint failure | Stop affected query, alert, restore and replay from immutable input | Yes, bounded |
| Review authorization failure | Return non-disclosing denial and append security audit | No |
| Idempotency conflict | HTTP 409/domain rejection; preserve original result | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `watermark` | ISO-8601 duration | `PT24H` | Maximum initial event-time delay |
| `tolerances[].absolute` | Decimal string | `"0.01"` | Approved comparison tolerance |
| `materiality.review/high/critical` | Decimal string | governed synthetic values | Severity boundaries |
| `checkpointRoot` | secret-free path | environment-specific | Isolated durable checkpoint root |
| `queryTrigger` | ISO-8601 duration | `PT1M` | Micro-batch target |
| `criticalRequiresHumanReview` | boolean | `true` | Mandatory critical gate |
| `autoCloseCritical` | boolean | `false` | Must remain false |
| `policyVersion/checksum` | strings | required | Reproducible configuration identity |

---

## Security Considerations

- Tenant and CNPJ predicates are applied before join, aggregation, lookup or review; PostgreSQL tables enable and force RLS.
- Cross-tenant identifiers return a non-disclosing not-found/denied response and create a security audit event.
- Company tax IDs are protected/tokenized in analytics; UI and logs display only authorized masked forms.
- All input identities and policy/source artifacts are integrity checked; no credentials or query parameters are accepted in official links.
- Review transitions require explicit roles, immutable actor/time/justification/evidence and four-eyes separation where configured.
- Critical cases cannot be auto-closed; this wave never calls settlement, fiscal issuance or legal-source endpoints.
- Cloud storage, checkpoints and databases use encryption, least privilege and tenant-scoped service identities.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured JSON with tenant-safe correlation, source/event version, policy checksum, cutoff and disposition; no raw sensitive payload |
| Metrics | Input/accepted/duplicate/quarantine/late counts, state size, match rate, divergence by type/severity, materiality, aging, recurrence, p95 detection and review SLA |
| Tracing | OpenTelemetry across ingestion/reconciliation/outbox/query with reconciliation and fingerprint identifiers |
| Alerts | Freshness >5 min, missing provenance, critical queue SLA, checkpoint failure, state growth and any completeness imbalance |
| Audit | Immutable replay, review transition, access denial and policy-version records |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Fiscal CDF] --\
[ERP CDF] -----+--> [Canonical ledger + DQ] --> [Dedup + watermark]
[Payment CDF] -+                                  |
[Split CDF] ---/                          [Stateful correlation]
[Tax Gold] ---------------------------------------+
                                                    |
                                 [Shadow compare + policy]
                                      /             \
                         [Reconciliation Gold] [Divergence Gold]
                                      \             /
                                [Metrics + Review Outbox]
                                          |
                                   [API / Control Tower]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| `shadow_event_ledger` | `event_date` | daily | Bounded replay and retention; cluster by tenant/transaction |
| `shadow_reconciliation` | `detected_date` | daily | History and operational-period queries; cluster by tenant/CNPJ |
| `shadow_divergence` | `detected_date` | daily | Aging/severity scans; cluster by tenant/status |
| `shadow_late_event` | `received_date` | daily | Controlled replay backlog |
| `shadow_metrics` | `metric_date` | daily | Dashboard period pruning |

Tenant is a clustering and mandatory predicate key, not a high-cardinality physical partition.

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Canonical ledger | Delta CDF append + idempotent event key | `event_id,event_version` | checkpoint + 24h recovery |
| Correlation | Stateful event-time incremental | canonical correlation key | policy watermark |
| Reconciliation/divergence | Append new semantic version/fingerprint | `reconciliation_id,version` | affected keys only |
| Late replay | Explicit bounded CDF range | `commit_version` | approved interval |
| Metrics | Incremental recompute of affected dates | `detected_date` | watermark + 1 day |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Optional additive column | Contract minor version; nullable reader support | Readers ignore column |
| Required column | New contract major version and dual-read migration | Continue prior version |
| Type/semantic change | New field/version; never reinterpret old history | Repoint consumer to prior contract |
| Enum addition | Unknown-safe reader plus contract compatibility gate | Disable producer version |
| Column removal | Deprecate for at least one major cycle; views retain alias | Restore compatibility view |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Tenant, source, event ID/version and event time non-null | Spark expectations/contract test | 0 invalid in publishable stream | Quarantine and block affected publication |
| Event accounting | Ledger reconciliation | input = accepted + duplicate + quarantined + late | Stop/alert on any imbalance |
| Monetary scale/currency | Decimal schema validation | 100% valid | Quarantine |
| Tax provenance | Gold expectation | 100% tax divergences have simulation/rule/memory/source | Block row and alert |
| Critical workflow | SQL/property test | 100% critical pending human review; 0 auto-close | Block release |
| Tenant isolation | RLS/adversarial tests | 0 cross-tenant disclosures | Block release |
| Replay parity | Fingerprint/checksum comparison | 100% semantic equality | Block release |
| Freshness | Streaming progress metrics | p95 <=5 min | Alert; block performance gate |
| Golden detection | pytest/Spark parity | 100% inserted divergence; 0 critical false match | Block release |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | design-agent | Initial Wave 5 architecture, manifest, governance and test gates |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_SHADOW_TAX_TAXFLOW_360.md`
