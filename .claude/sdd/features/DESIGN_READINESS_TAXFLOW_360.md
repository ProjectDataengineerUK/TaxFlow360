# DESIGN: Diagnóstico de Prontidão TaxFlow 360

> Technical design for deterministic, explainable and versioned Tax Readiness assessments

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | READINESS_TAXFLOW_360 |
| **Date** | 2026-08-14 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_READINESS_TAXFLOW_360.md](./DEFINE_READINESS_TAXFLOW_360.md) |
| **Parent DESIGN** | [DESIGN_PLATAFORMA_TAXFLOW_360.md](./DESIGN_PLATAFORMA_TAXFLOW_360.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
Canonical accepted transactions + company/source inventory
                         |
                         v
               [Eligibility Gate]
                  |           |
             ineligible    eligible
                  |           |
                  v           v
            [Draft issues] [Methodology 1.0]
                                |
                 +--------------+---------------+
                 |              |               |
                 v              v               v
             [Evidence]   [8 Dimensions]  [Recommendations]
                 |              |               |
                 +--------------+---------------+
                                |
                                v
                   [Immutable Assessment]
                       |               |
                       v               v
                 [Query API]      [Control Tower]

Execution: local deterministic engine for tests + equivalent Databricks Gold pipeline
```

The methodology is configuration-as-data. A pure Python domain engine provides fast deterministic tests and reference behavior. The Databricks pipeline implements the same rule contract over Silver data and publishes immutable Delta assessments. The Query API only exposes published results after applying tenant/CNPJ authorization.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Readiness Methodology Contract | Version, dimensions, weights, thresholds and evidence rules | YAML + Pydantic |
| Eligibility Gate | Prevent official score when minimum evidence is absent | Python/PySpark |
| Reference Scoring Engine | Deterministic local calculation and golden oracle | Python, Decimal |
| Evidence Evaluator | Convert quality facts into positive/negative evidence | Python/PySpark expressions |
| Readiness Gold Pipeline | Aggregate scores and persist immutable assessments | Databricks, PySpark, Delta |
| Assessment Repository | Tenant-scoped published/history access | Python protocol + in-memory/local implementation for wave tests |
| Query API | Latest, history and comparison endpoints | FastAPI |
| Control Tower Readiness | General/dimensional score, risks and actions | Next.js, TypeScript |
| Readiness Test Suite | Formula, API, history, isolation and 100k SLA | pytest |

---

## Key Decisions

### Decision 1: Metodologia versionada como dados

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** Weights and thresholds will change and every historical score must remain reproducible.

**Choice:** Store the methodology in reviewed YAML with immutable semantic version, exactly eight dimensions, decimal weights summing to 1.0, eligibility requirements and recommendation mappings.

**Rationale:** Separates governance from deployment while preserving a human-reviewable and testable artifact.

**Alternatives Rejected:**
1. Hardcoded weights in PySpark — difficult to govern and reproduce.
2. LLM-generated scoring — non-deterministic and unsuitable for official assessment.

**Consequences:**
- CI blocks invalid weights, missing dimensions and breaking changes.
- Published assessments retain methodology version and checksum.

---

### Decision 2: Evidence facts before scores

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** A score without traceable facts is not defensible to fiscal teams or auditors.

**Choice:** Compute normalized evidence facts first; dimension rules consume those facts and emit contribution, severity and recommendation. The overall score is only an aggregation of dimension scores.

**Rationale:** Enables lineage, debugging and explanation without rereading raw payloads.

**Alternatives Rejected:**
1. Aggregate directly from transactions — loses the explanation layer.
2. Store only final score — prevents audit and temporal comparison.

**Consequences:**
- Evidence IDs become part of the assessment contract.
- Missing evidence is explicit and can make an assessment ineligible.

---

### Decision 3: Reference engine defines semantic parity

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-14 |

**Context:** Local tests must run without Databricks while the production pipeline uses distributed processing.

**Choice:** Implement a pure Python reference engine using Decimal and a PySpark pipeline that consumes the same methodology. Golden fixtures compare their outputs.

**Rationale:** Provides rapid tests and a stable oracle for the distributed implementation.

**Alternatives Rejected:**
1. PySpark-only logic — makes unit tests slow and workspace-dependent.
2. Separate formulas — creates silent semantic drift.

**Consequences:**
- Formula changes require parity tests.
- Unsupported rule operators are rejected by both engines.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `contracts/data/readiness-assessment.contract.yaml` | Create | Output contract, lineage and SLA | @data-quality-analyst | None |
| 2 | `config/readiness-methodology.yaml` | Create | Versioned eight-dimension methodology | @especialista-tributario | None |
| 3 | `services/query-service/src/taxflow_query/readiness.py` | Create | Domain models and reference engine | @python-developer | 1, 2 |
| 4 | `services/query-service/src/taxflow_query/repository.py` | Create | Tenant-scoped immutable repository | @python-developer | 3 |
| 5 | `services/query-service/src/taxflow_query/api.py` | Modify | Latest, history and comparison endpoints | @python-developer | 3, 4 |
| 6 | `data/databricks/resources/readiness.yml` | Create | Readiness job/pipeline bundle resource | @lakeflow-architect | 1, 2 |
| 7 | `data/databricks/src/readiness_methodology.py` | Create | Load and validate methodology in Spark | @databricks-spark-expert | 2, 6 |
| 8 | `data/databricks/src/gold_readiness.py` | Modify | Evidence, dimensions and immutable Gold output | @databricks-spark-expert | 1, 7 |
| 9 | `apps/control-tower/src/app/readiness/page.tsx` | Create | Readiness score and actions view | @ecc-typescript-reviewer | 5 |
| 10 | `tests/readiness/test_methodology.py` | Create | Weights, dimensions and deterministic scoring | @test-generator | 2, 3 |
| 11 | `tests/readiness/test_readiness_api.py` | Create | Latest/history/comparison and tenant isolation | @test-generator | 4, 5 |
| 12 | `tests/readiness/test_readiness_parity.py` | Create | Reference fixtures for Spark parity | @data-quality-analyst | 3, 7, 8 |
| 13 | `tests/readiness/test_readiness_performance.py` | Create | 100k assessment time gate | @spark-performance-analyzer | 3 |
| 14 | `.github/workflows/ci.yml` | Modify | Add Readiness unit/contract gates | @ecc-code-architect | 1-13 |

**Total Files:** 14

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @data-quality-analyst | 1, 12 | Contracts, lineage and parity evidence |
| @especialista-tributario | 2 | Tax readiness dimensions and governed methodology |
| @python-developer | 3-5 | Typed domain engine, repository and FastAPI |
| @lakeflow-architect / @databricks-spark-expert | 6-8 | Bundle resources, Delta and PySpark |
| @ecc-typescript-reviewer | 9 | Next.js view and typed client boundary |
| @test-generator / @spark-performance-analyzer | 10, 11, 13 | Functional, isolation and SLA tests |
| @ecc-code-architect | 14 | CI gates and dependency ordering |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: File type, purpose keywords, path patterns, KB domains

---

## Code Patterns

### Pattern 1: Decimal weighted score

```python
from decimal import Decimal, ROUND_HALF_EVEN


def weighted_score(scores: dict[str, Decimal], weights: dict[str, Decimal]) -> Decimal:
    if scores.keys() != weights.keys():
        raise ValueError("scores and weights must contain the same dimensions")
    if sum(weights.values(), Decimal()) != Decimal("1"):
        raise ValueError("weights must sum to 1")
    total = sum((scores[name] * weights[name] for name in scores), Decimal())
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
```

### Pattern 2: Immutable assessment identity

```python
from hashlib import sha256
from json import dumps


def assessment_fingerprint(tenant_id: str, company_tax_id: str, cutoff_at: str, methodology_version: str) -> str:
    payload = {
        "tenant_id": tenant_id,
        "company_tax_id": company_tax_id,
        "cutoff_at": cutoff_at,
        "methodology_version": methodology_version,
    }
    return sha256(dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
```

### Pattern 3: Configuration Structure

```yaml
methodology:
  version: 1.0.0
  status: draft
  dimensions:
    fiscal:
      weight: 0.15
      minimum_evidence: 1
  thresholds:
    critical: 50
    attention: 75
    ready: 90
```

---

## Data Flow

```text
1. Silver transactions and source/company inventory reach cutoff
   |
   v
2. Eligibility gate records included/excluded counts and missing requirements
   |--- ineligible ---> draft issues, no official score
   `--- eligible
          |
          v
3. Evidence facts are computed with stable IDs and source lineage
   |
   v
4. Methodology rules calculate eight dimension scores
   |
   v
5. Decimal weights produce overall score and classification
   |
   v
6. Immutable assessment, evidence and recommendations are written to Gold
   |
   v
7. Query API filters by authorized tenant/CNPJ and serves latest/history/diff
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Foundation Silver contract | Delta tables/files | Unity Catalog identity in workspace |
| Databricks job | Declarative Automation Bundle | Workload identity/service principal |
| Query API | Repository/Databricks SQL adapter | Workload identity; tenant context from OIDC boundary |
| Control Tower | REST/JSON | OIDC session and API scopes |
| Methodology approver | Reviewed Git change in this wave | Protected branch approval |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Formula, eligibility, classification and recommendations | `tests/readiness/test_methodology.py` | pytest | 100% rule operators and dimensions |
| Contract | Assessment fields, exactly eight dimensions, lineage | Contract/parity tests | pytest + YAML parser | 100% required fields |
| API | Latest, history, diff and negative tenant access | `test_readiness_api.py` | pytest/FastAPI client | All endpoints and denial paths |
| Parity | Reference vs expected Spark result | `test_readiness_parity.py` | pytest fixtures | 100% exact decimals/evidence IDs |
| Performance | 100k canonical facts | `test_readiness_performance.py` | pytest benchmark/timer | ≤15 minutes; local target recorded |
| Databricks integration | Silver → Gold publication/history | Test workspace | Bundle validate/run | R-AT-001..009 applicable paths |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Invalid methodology | Block load/CI with exact field and invariant | No |
| Ineligible evidence | Persist draft issues; never publish official score | No |
| Unknown rule operator | Reject methodology version | No |
| Duplicate fingerprint | Return existing assessment idempotently | No effect |
| Transient Delta/SQL failure | Bounded retry with same assessment fingerprint | Yes |
| Cross-tenant request | Deny without resource disclosure and audit | No |
| Parity mismatch | Block promotion of methodology/pipeline | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `methodology.version` | semver | `1.0.0` | Immutable formula version |
| `methodology.status` | enum | `draft` | Draft cannot publish official assessments |
| `methodology.dimensions.*.weight` | decimal | Per approved config | Must sum exactly to 1 |
| `methodology.dimensions.*.minimum_evidence` | int | `1` | Eligibility per dimension |
| `methodology.thresholds.critical` | decimal | `50` | Upper bound of critical |
| `methodology.thresholds.attention` | decimal | `75` | Attention boundary |
| `methodology.thresholds.ready` | decimal | `90` | Ready boundary |
| `readiness.cutoff_timezone` | string | `UTC` | Logical cutoff normalization |

---

## Security Considerations

- Tenant and authorized CNPJs come from trusted identity context, not query parameters alone.
- Repository methods require tenant as a mandatory key and never expose global lookup.
- Company tax IDs are masked in logs and protected in Gold/query outputs by role.
- Evidence references use stable IDs; sensitive raw payload is not copied into assessment records.
- Published methodology requires protected review; runtime cannot promote draft configuration.
- Assessment history is append-only and changes produce a new fingerprint/version.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Assessment ID, methodology, tenant pseudonym, CNPJ mask, cutoff and status |
| Metrics | Duration, eligible/excluded rows, published/draft counts, score distribution and API denials |
| Tracing | Ingestion batch/cutoff → Gold assessment → API request |
| Data quality | Evidence completeness, eight-dimension invariant, reproducibility and parity |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Silver Transactions] ─┐
[Source Inventory] ─────┼→ [Eligibility] → [Evidence Facts] → [Dimension Scores]
[Company Profile] ──────┘         |                                  |
                                  v                                  v
                            [Draft Issues]                 [Weighted Assessment]
                                                                      |
                                                                      v
                                                            [Gold + History/API]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| `readiness_evidence` | `assessment_date` | Monthly | Audit/time filtering; cluster by tenant/CNPJ |
| `readiness_assessment` | `assessment_date` | Monthly | History and latest lookup; cluster by tenant/CNPJ |
| `readiness_recommendation` | `assessment_date` | Monthly | Join by assessment and priority |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Evidence facts | Recompute for explicit cutoff | `assessment_id`, `evidence_id` | Closed dataset only |
| Dimension scores | Append immutable result | `assessment_id`, `dimension` | None |
| Assessment | Idempotent insert by fingerprint | `assessment_id`/fingerprint | None |
| Latest view | Window by published timestamp/version | tenant + CNPJ | Full history metadata only |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Add evidence attribute | Optional minor contract version | Readers ignore new field |
| Change weight/threshold | New methodology version | Reuse prior version for existing assessments |
| Add/remove dimension | Major methodology and contract version | Keep v1 eight-dimension pipeline active |
| Change score type/scale | Parallel column and compatibility window | Restore prior view |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Dimension count | pytest/Lakeflow | Exactly 8 per published assessment | Block publication |
| Weight sum | Pydantic/Decimal | Exactly 1.0 | Block methodology |
| Score range | pytest/Lakeflow | 0..100 | Block publication |
| Evidence coverage | Lakeflow | 100% contributions explained | Draft/block publication |
| Reproducibility | pytest/checksum | 100% identical | Block CI |
| Tenant isolation | API/security tests | Zero bypass | Block CI/release |
| SLA | Pipeline metrics | ≤15 minutes for 100k | Block Ship |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-14 | design-agent | Initial Readiness wave technical design |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_READINESS_TAXFLOW_360.md`
