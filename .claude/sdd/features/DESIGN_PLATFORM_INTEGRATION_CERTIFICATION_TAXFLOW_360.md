# DESIGN: Integração e Certificação da Plataforma TaxFlow 360

> Technical design for implementing Integração e Certificação da Plataforma TaxFlow 360

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360.md](./DEFINE_PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360.md) |
| **Status** | Ready for Build |
| **Design Confidence** | 0.95 — testing/Terraform/Spark/streaming/lakehouse KB patterns and specialist agents found |

---

## Architecture Overview

```text
                         [Commit / Candidate Tag]
                                   |
                   [Tier 1: deterministic fast CI]
 contracts -> Python -> JVM -> TypeScript -> static security -> artifact hashes
                                   |
                         [Candidate manifest]
                                   |
             +---------------------+---------------------+
             |                     |                     |
 [Tier 2: ephemeral app] [Tier 2: Databricks] [Tier 2: cloud plans]
 Postgres/services/UI     CDF/stream/RAG/MLflow  AWS | Azure | GCP
             \                     |                     /
              +------------ [E2E synthetic journey] ----+
                                   |
                  [Security + resilience + performance]
                                   |
                     [Evidence ledger: PASS/FAIL/BLOCKED]
                                   |
                [Human gates: tax catalog + regulatory corpus]
                                   |
                       [Go/No-Go policy evaluator]
                           /                 \
                    [BLOCKED/FAIL]      [Signed RC]
                     no promotion       immutable artifacts
```

Certification orchestration reads test outputs and creates evidence; it does not reimplement domain logic. Environments are provisioned only by approved workflows with budgets and are destroyed after evidence capture. Promotion is a pure policy decision over immutable gate records.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Toolchain manifest | Pin language, build, Terraform and Databricks versions | `.tool-versions`, Gradle wrapper, npm lock, Python constraints |
| Certification contract | Define run/gate/evidence/status schema | ODCS/YAML/JSON Schema |
| Gate registry | Required/optional gates, owners, tiers, timeouts and evidence rules | Approved YAML |
| Candidate builder | Build immutable artifacts, checksums, SBOM and manifest | GitHub Actions, Gradle, npm, Python |
| Environment orchestrator | Create/identify ephemeral app, Databricks and cloud-plan targets | Python CLI + Terraform/Databricks CLI |
| E2E driver | Generate synthetic tenant operations and follow correlation IDs through six products | pytest/FastAPI clients |
| Conformance suites | Contract, parity, tenancy, provenance, cloud and runtime invariants | pytest/JUnit/Playwright/Terraform test |
| Evidence collector | Normalize JUnit/SARIF/JSON/plan/metrics into immutable gate results | Python/Pydantic |
| Evidence ledger | Append-only run/gate/evidence records with hashes | JSON artifacts + object storage/Delta in hosted CI |
| Policy evaluator | Permit RC only when every required gate is PASS with valid evidence | Deterministic Python |
| Human approval | Sign tax catalog/corpus decisions with separate authorized actors | GitHub Environment/transactional approval adapter |
| RC attestor | Publish checksums, SBOM, signatures and provenance for the exact commit | CI OIDC + artifact registry signing |

---

## Key Decisions

### Decision 1: Three certification tiers with no inferred PASS

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Fast feedback and hosted integration have different cost, latency and credential requirements. Today unavailable runtimes are known blockers and must not be hidden.

**Choice:** Tier 1 runs deterministic local-compatible checks on every commit; Tier 2 runs app/Databricks/cloud integration for a candidate; Tier 3 runs security, resilience, performance and human approvals. Every registered gate ends as `PASS`, `FAIL`, `BLOCKED` or explicitly approved `SKIPPED_WITH_APPROVAL`. Missing execution defaults to `BLOCKED`.

**Rationale:** Separating tiers keeps ordinary CI useful while preserving rigorous release semantics. A finite registry makes completeness machine-checkable; evidence, rather than workflow success alone, proves a pass.

**Alternatives Rejected:**
1. Single monolithic workflow — rejected because cloud cost/failure would block all developer feedback.
2. Treat unavailable infrastructure as skipped/pass — rejected because it recreates the current certification gap.
3. Free-form release checklist — rejected because omissions cannot be detected automatically.

**Consequences:**
- A release remains blocked until environments and people are available.
- The dashboard distinguishes product failure from unavailable external prerequisites.

---

### Decision 2: Evidence ledger is append-only and content-addressed

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** CI logs expire and can be rerun against different commits/configuration. Audit requires proof of exactly what passed.

**Choice:** Each gate record binds RC commit, tool versions, dataset/config/cutoff, environment, timestamps, raw evidence URI and SHA-256. New attempts append versions; they never overwrite prior outcomes. The final matrix checksum is included in the RC manifest.

**Rationale:** Content-addressed evidence makes tampering and accidental mismatch detectable and lets auditors reproduce the conditions of promotion.

**Alternatives Rejected:**
1. Link only to workflow page — rejected because retention and mutable reruns are insufficient.
2. Store only summarized PASS/FAIL — rejected because the claim cannot be independently checked.

**Consequences:**
- Evidence storage and retention need lifecycle/governance.
- Redaction occurs before upload; evidence cannot contain secrets or raw sensitive payloads.

---

### Decision 3: Ephemeral environments with plan-only multi-cloud certification by default

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Deploying three full clouds per candidate is costly and requires authority beyond implementation; portability still needs proof.

**Choice:** Run `fmt/validate/test/plan` against provider sandboxes for AWS/Azure/GCP, with policy checks on encryption, versioning, identity, tags and residency. Apply occurs only in the explicitly selected certification cloud after budget/approval; other providers remain plan-certified. Environments carry TTL and teardown verification.

**Rationale:** Plans verify portable module contracts without unauthorized spend. One applied target proves runtime integration; periodic/edition-specific applied tests may cover the others separately.

**Alternatives Rejected:**
1. Apply all providers automatically — rejected due to cost and destructive/external state.
2. Validate syntax only — rejected because provider configuration/policies need realistic plans.

**Consequences:**
- “Plan-certified” and “runtime-certified” are distinct labels.
- Provider credentials, budgets and regions are explicit prerequisites, never inferred.

---

### Decision 4: One canonical E2E synthetic journey with domain-owned assertions

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Each wave passes isolated tests, but duplicated integration expectations would drift from domain engines.

**Choice:** A versioned fixture emits canonical transactions for two tenants and traces them across ingestion, readiness, simulation, Digital Twin, Shadow Tax and Regulatory AI. E2E verifies identities and cross-product invariants; detailed calculations remain asserted by each wave’s golden suite.

**Rationale:** This proves composition without creating a second tax engine in test code.

**Alternatives Rejected:**
1. Recalculate every tax value inside E2E — rejected due to duplicated logic.
2. Test only HTTP 2xx — rejected because lineage, citations and monetary parity could be wrong.

**Consequences:**
- Fixture/schema changes require contract review.
- Failures route to the owning wave and rerun its build gates before recertification.

---

### Decision 5: Release candidate promotion is deterministic and human gates are explicit

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Security and domain approval cannot be replaced by an aggregate score or model confidence.

**Choice:** `evaluate_release()` requires every mandatory technical gate to be PASS and designated tax/security approvals to carry distinct authorized actors. No weighted score, waiver-by-default or AI approval exists. It emits an attestation only for the exact candidate manifest.

**Rationale:** Binary policy avoids compensating a critical failure with unrelated successes and preserves separation of duties.

**Alternatives Rejected:**
1. Readiness percentage threshold — rejected because critical controls are non-compensable.
2. Allow administrators to self-approve all gates — rejected because four-eyes is required.

**Consequences:**
- RC creation may wait for reviewers.
- Emergency exceptions require a separately designed, time-bounded governance process and are out of this wave.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `.tool-versions` | Create | Pin Java, Python, Node, Terraform and Databricks CLI | @ci-cd-specialist | None |
| 2 | `gradle/wrapper/gradle-wrapper.properties` | Create | Pin Gradle distribution/checksum | @ecc-java-build-resolver | 1 |
| 3 | `gradlew` | Create | Unix wrapper entry | @ecc-java-build-resolver | 2 |
| 4 | `gradlew.bat` | Create | Windows wrapper entry | @ecc-java-build-resolver | 2 |
| 5 | `package-lock.json` | Create | Root/workspace frontend dependency lock | @ecc-typescript-reviewer | 1 |
| 6 | `constraints-certification.txt` | Create | Pin Python certification dependencies | @python-developer | 1 |
| 7 | `contracts/data/certification-run.contract.yaml` | Create | Gate/evidence ledger ODCS | @data-contracts-engineer | None |
| 8 | `config/certification-gates.yaml` | Create | Tiered required gates, owners, timeouts and evidence | @data-governance-auditor | 7 |
| 9 | `config/certification-environments.yaml` | Create | Environment capabilities, budgets, TTL and labels without secrets | @data-platform-security | 8 |
| 10 | `tools/certification/pyproject.toml` | Create | Self-contained orchestration package | @python-developer | 6 |
| 11 | `tools/certification/src/taxflow_certification/models.py` | Create | Immutable candidate/gate/evidence models | @python-developer | 7,8 |
| 12 | `tools/certification/src/taxflow_certification/registry.py` | Create | Strict gate/environment loader/checksum | @python-developer | 8,9,11 |
| 13 | `tools/certification/src/taxflow_certification/evidence.py` | Create | Hash, redact and normalize evidence | @ecc-security-reviewer | 11,12 |
| 14 | `tools/certification/src/taxflow_certification/policy.py` | Create | Deterministic go/no-go evaluation | @data-governance-auditor | 11-13 |
| 15 | `tools/certification/src/taxflow_certification/cli.py` | Create | Initialize/record/evaluate/finalize commands | @python-developer | 11-14 |
| 16 | `tests/e2e/fixtures/platform-journey.yaml` | Create | Two-tenant cross-product synthetic journey | @test-generator | 7,8 |
| 17 | `tests/e2e/test_platform_journey.py` | Create | Full lineage, outputs and official citations | @test-generator | 10-16 |
| 18 | `tests/conformance/test_contract_compatibility.py` | Create | ODCS/Avro/OpenAPI refs and evolution | @data-contracts-engineer | 7,8 |
| 19 | `tests/conformance/test_cross_tenant_matrix.py` | Create | API/repository/analytics/vector isolation matrix | @ecc-security-reviewer | 16 |
| 20 | `tests/conformance/test_tax_parity.py` | Create | JVM/reference/lakehouse golden parity adapter | @test-generator | 16 |
| 21 | `tests/conformance/test_official_provenance.py` | Create | Rule/memory/source/citation chain | @especialista-tributario | 16 |
| 22 | `tests/conformance/test_cloud_contract.py` | Create | Common AWS/Azure/GCP plan invariants | @data-platform-security | 9 |
| 23 | `tests/resilience/test_replay_recovery.py` | Create | Checkpoint, outbox, backup and replay | @spark-streaming-architect | 16 |
| 24 | `tests/resilience/test_dependency_failures.py` | Create | Database/search/model/stream fault behavior | @ecc-security-reviewer | 16 |
| 25 | `tests/performance/test_integrated_100k.py` | Create | Cross-product accounting/SLO evidence | @ecc-performance-optimizer | 16 |
| 26 | `deploy/terraform/certification/main.tf` | Create | Ephemeral environment composition and policies | @data-platform-engineer | 9 |
| 27 | `deploy/terraform/certification/variables.tf` | Create | Cloud/region/budget/TTL inputs and validation | @data-platform-engineer | 9,26 |
| 28 | `deploy/terraform/certification/outputs.tf` | Create | Non-secret endpoints/evidence metadata | @data-platform-engineer | 26,27 |
| 29 | `data/databricks/resources/certification.yml` | Create | Hosted bundle validation, streaming/RAG/evaluation tasks | @lakeflow-architect | 8,9,16 |
| 30 | `.github/workflows/ci-fast.yml` | Create | Tier 1 matrix and immutable candidate manifest | @ci-cd-specialist | 1-8,10-15 |
| 31 | `.github/workflows/certification-hosted.yml` | Create | Approved Tier 2/3 orchestration and evidence | @ci-cd-specialist | 8-29 |
| 32 | `.github/workflows/release-candidate.yml` | Create | Policy check, SBOM/signing/attestation, no deploy | @ci-cd-specialist | 11-15,30,31 |
| 33 | `.github/dependency-review-config.yml` | Create | Critical dependency policy | @ecc-security-reviewer | 30 |
| 34 | `docs/runbooks/certification.md` | Create | Operators, prerequisites, costs, teardown and blockers | @code-documenter | 8,9,26-32 |
| 35 | `docs/runbooks/recovery.md` | Create | Backup/checkpoint/outbox recovery procedures | @code-documenter | 23,29 |
| 36 | `.claude/sdd/reports/CERTIFICATION_MATRIX_TEMPLATE.md` | Create | Human-readable go/no-go evidence template | @data-governance-auditor | 7,8,11 |

**Total Files:** 36

---

## Agent Assignment Rationale

> Agents discovered from `.claude/agents/`; Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @ci-cd-specialist | 1,30-32 | Toolchains, workflows, promotion and attestations |
| @ecc-java-build-resolver | 2-4 | Gradle/JVM reproducibility |
| @ecc-typescript-reviewer | 5 | npm workspace lock integrity |
| @python-developer | 6,10-12,15 | Certification CLI and typed orchestration |
| @data-contracts-engineer | 7,18 | Evidence contract and compatibility |
| @data-governance-auditor | 8,14,36 | Gate policy, approvals and matrix |
| @data-platform-security | 9,22 | Environment/cloud security invariants |
| @ecc-security-reviewer | 13,19,24,33 | Evidence redaction, tenancy and supply chain |
| @test-generator | 16,17,20 | Deterministic E2E/parity tests |
| @especialista-tributario | 21 | Official provenance/domain review boundary |
| @spark-streaming-architect | 23 | Replay/checkpoint semantics |
| @ecc-performance-optimizer | 25 | Integrated load/SLO evidence |
| @data-platform-engineer | 26-28 | Ephemeral certification IaC |
| @lakeflow-architect | 29 | Hosted Databricks orchestration |
| @code-documenter | 34,35 | Operational and recovery runbooks |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: file type, purpose, path and DEFINE KB domains

---

## Code Patterns

### Pattern 1: Missing gates are BLOCKED

```python
from enum import StrEnum

class GateStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    SKIPPED_WITH_APPROVAL = "SKIPPED_WITH_APPROVAL"

def complete_matrix(required_gate_ids: set[str], recorded: dict[str, "GateResult"]):
    return {
        gate_id: recorded.get(gate_id, GateResult.blocked(gate_id, "no evidence recorded"))
        for gate_id in sorted(required_gate_ids)
    }
```

### Pattern 2: Evidence hash binds exact bytes

```python
from hashlib import sha256
from pathlib import Path

def evidence_digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
```

### Pattern 3: Configuration Structure

```yaml
version: 1.0.0
status: approved
tiers:
  - id: fast
    gates:
      - id: contracts
        required: true
        owner: data-contracts
        evidenceType: junit
        timeoutMinutes: 5
  - id: hosted
    gates:
      - id: databricks-streaming
        required: true
        owner: data-platform
        evidenceType: json
        requiredCapabilities: [unity_catalog, cdf, serverless]
promotion:
  missingGateStatus: BLOCKED
  failOnRequiredSkipped: true
  humanApprovals: [tax_catalog, regulatory_corpus, security]
```

### Pattern 4: Non-compensable release policy

```python
def evaluate_release(matrix, approvals, candidate_sha: str):
    blockers = [gate.id for gate in matrix if gate.required and gate.status != "PASS"]
    if blockers:
        return Decision("BLOCKED", tuple(blockers), candidate_sha)
    if approvals["tax_catalog"].actor_id == approvals["regulatory_corpus"].actor_id:
        return Decision("BLOCKED", ("independent domain approvals required",), candidate_sha)
    return Decision("APPROVED_FOR_RC", (), candidate_sha)
```

---

## Data Flow

```text
1. Commit and lockfiles define a candidate manifest/checksum.
   |
2. Tier 1 builds/tests each runtime and records content-addressed evidence.
   |
3. Approved dispatch provisions or selects ephemeral hosted targets.
   |
4. Synthetic E2E journey emits canonical two-tenant transactions.
   |
5. App, Databricks and cloud-plan suites record metrics/reports/checksums.
   |
6. Security, resilience, recovery and 100k suites append gate outcomes.
   |
7. Independent specialists attach catalog/corpus/security decisions.
   |
8. Policy fills missing gates as BLOCKED and evaluates go/no-go.
   |
9. Only an all-green matrix produces signed RC artifacts; teardown is verified.
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| GitHub Actions/Environments | Workflow, artifacts, approvals, OIDC | Repository roles + OIDC federation |
| Artifact/container registry | Images, SBOM, checksums, signatures | Short-lived OIDC identity |
| AWS/Azure/GCP sandboxes | Terraform plan and selected ephemeral apply | Provider workload identity; no static keys |
| Databricks test workspace | Bundle deploy/run, Delta/CDF, MLflow, AI Search | Workload identity/service principal |
| PostgreSQL/Redis/Kafka-compatible test services | Ephemeral integration runtime | Generated scoped test credentials |
| Security scanners | SARIF/SBOM/IaC/image reports | CI-local or approved service identity |
| Human reviewers | Protected environment approvals | Enterprise SSO + role mapping |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Registry, evidence hash/redaction and policy | 11-15 | pytest/Hypothesis | Missing=BLOCKED; immutable evidence |
| Contract | ODCS/Avro/OpenAPI/producer-consumer compatibility | 7,18 | pytest/schema validators | IC-AT-002 |
| E2E | Six-product journey and provenance | 16,17,21 | pytest/HTTP clients | IC-AT-003,008 |
| Security | Tenant matrix, SAST/SCA/secrets/SBOM/IaC/RAG | 19,22,24,30-33 | pytest/SARIF/scanners | IC-AT-004,009 |
| Parity | Kotlin/reference/PySpark | 20 | JUnit/pytest/Databricks | IC-AT-005 |
| Resilience | Replay, faults, backup/restore | 23,24,35 | pytest/chaos adapters | IC-AT-006,007,017 |
| Cloud | AWS/Azure/GCP fmt/validate/test/plan | 22,26-28,31 | Terraform | IC-AT-010-012 |
| Databricks | Streaming/CDF/AI Search/MLflow | 29,31 | Databricks CLI/pytest | IC-AT-013,014 |
| Performance | Integrated 100k | 25,31 | pytest/hosted metrics | IC-AT-016 |
| Release | Toolchain, human approvals, attestation and blocked gate | 1-15,30-32 | CI/registry | IC-AT-001,015,018,019 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Tool/runtime unavailable | Record BLOCKED with prerequisite; never PASS | After environment changes |
| Test assertion/security finding | Record FAIL with immutable raw evidence | Only after new candidate/fix |
| Transient hosted outage | Bounded retry under same candidate/environment; append attempts | Yes, bounded |
| Evidence upload/hash mismatch | Mark gate FAIL/BLOCKED; prohibit promotion | Once after integrity check |
| Credential/budget/approval missing | Do not provision; record BLOCKED | After explicit authorization |
| Terraform partial apply | Stop, capture state/plan, follow runbook and verify teardown | Controlled only |
| E2E lineage gap | FAIL owning integration gate; route to wave owner | New build required |
| Human reviewer conflict | Reject approval and keep gate BLOCKED | Different authorized actor |
| Teardown failure | Alert, preserve state/evidence and block RC | Controlled recovery |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `tiers[].gates[].required` | boolean | explicit | Non-compensable gate flag |
| `missingGateStatus` | enum | `BLOCKED` | Safety default |
| `timeoutMinutes` | integer | per gate | Bounded execution |
| `environment.ttlHours` | integer | `8` | Ephemeral lifetime |
| `environment.maxBudget` | decimal string | approval-defined | Cost guard |
| `loadProfile` | enum | `100k` | Initial RC profile |
| `evidenceRetentionDays` | integer | `2555` | Audit retention |
| `candidateCommit` | SHA | required | Exact source identity |
| `logicalCutoff` | timestamp | required | Deterministic data/model cutoff |
| `humanApprovals` | list | tax/security set | Required protected gates |

---

## Security Considerations

- Hosted workflows use protected environments, least-privilege OIDC identities, concurrency locks and explicit approval before cost/external state.
- Candidate code cannot modify gate registry or workflow and approve itself in the same unreviewed change; CODEOWNERS/environment rules enforce separation.
- Evidence is redacted before upload, scanned for secrets, hashed and stored immutably; raw fiscal/customer data is prohibited.
- Terraform plan/apply permissions are separate; plans are pinned to candidate/provider locks and applies use saved approved plans.
- All tenants in E2E are synthetic. Cross-tenant probes include APIs, RLS, caches, Delta, vector search, logs and metrics.
- Dependency/image/IaC critical findings block promotion. SBOM and provenance bind exact artifacts and source commit.
- Teardown never uses broad/unresolved targets; environment IDs/state are validated and retained for recovery if deletion fails.
- Human domain/security approvals require enterprise identity, role and different actors where four-eyes applies.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured certification/run/gate/candidate IDs; secrets and payloads redacted |
| Metrics | Gate duration/status/retry, environment cost/TTL, E2E SLO, resource usage and flake rate |
| Tracing | Correlation ID spans from synthetic ingress through six products and evidence collector |
| Alerts | Critical security failure, hosted timeout, budget threshold, teardown failure, evidence mismatch and approval aging |
| Audit | Append-only attempts, tool/environment versions, approvals, plan hashes, RC manifest/SBOM/signature |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Candidate commit]
       |
[Toolchain/contracts/builds] --> [Candidate manifest]
       |                              |
       +------------------------------+
                                      |
         +----------------------------+---------------------------+
         |                            |                           |
 [Ephemeral app stack]       [Databricks bundle]        [3 cloud plans]
         |                            |                           |
         +---------- [Synthetic E2E + conformance] --------------+
                                      |
                    [Security/resilience/performance]
                                      |
                      [Evidence normalize + checksum]
                                      |
                       [Human approval references]
                                      |
                            [Policy evaluation]
                              /             \
                         [BLOCKED]       [Signed RC]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| `certification_run` | `started_date` | daily | Audit/release-period pruning |
| `certification_gate_result` | `started_date` | daily | Gate history; cluster by candidate/gate |
| `certification_metric` | `metric_date` | daily | SLO/cost trend analysis |
| `certification_lineage` | `run_id` | run | Efficient E2E trace reconstruction |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Candidate manifest | One immutable record per commit/config checksum | `candidate_sha` | none |
| Gate result | Append attempt/version | `run_id,gate_id,attempt` | current run |
| Evidence | Content-addressed immutable object | `evidence_sha256` | none |
| Metrics | Append per gate execution | `run_id,gate_id,metric` | current run |
| Final matrix | Snapshot derived after required gates/humans | `run_id` | full run |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Add optional gate metadata | Contract minor version | Readers ignore field |
| New required gate | Registry version bump; old runs retain prior registry | Evaluate under prior checksum |
| Status semantic change | Contract major version; never reinterpret history | Continue previous evaluator |
| Evidence format change | New evidence type/parser with raw bytes retained | Reparse using old adapter |
| Gate removal | Deprecate with rationale; retain historic records | Restore registry entry |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Registered gate completeness | Policy evaluator | 100% statuses | Missing → BLOCKED |
| PASS evidence integrity | SHA-256 verification | 100% | FAIL promotion |
| Candidate identity | Manifest/commit hash | 100% match | Abort run |
| Synthetic event accounting | E2E ledger | input = all terminal dispositions | FAIL |
| Tenant isolation | Adversarial matrix | 0 disclosure | Critical FAIL |
| Monetary parity | Golden comparator | 100% | FAIL |
| Official provenance | Citation resolver | 100% | FAIL |
| Cloud policy | Terraform tests/plan scan | 100% mandatory invariants | FAIL/BLOCKED |
| Hosted SLO | Databricks/app metrics | Wave thresholds | FAIL |
| Security | SARIF/scanners | 0 critical/secrets | Critical FAIL |
| Human approvals | Identity/role validation | all distinct required actors | BLOCKED |
| Teardown | Environment inventory | 0 unintended live resources | Block close/alert |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | design-agent | Initial three-tier certification architecture, 36-file manifest and RC policy |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_PLATFORM_INTEGRATION_CERTIFICATION_TAXFLOW_360.md`
