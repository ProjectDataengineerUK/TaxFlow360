# DESIGN: Digital Twin Financeiro TaxFlow 360

> Technical design for deterministic cash-flow, tax-float, working-capital and governed forecast scenarios

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | DIGITAL_TWIN_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_DIGITAL_TWIN_TAXFLOW_360.md](./DEFINE_DIGITAL_TWIN_TAXFLOW_360.md) |
| **Parent DESIGN** | [DESIGN_PLATAFORMA_TAXFLOW_360.md](./DESIGN_PLATAFORMA_TAXFLOW_360.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
Canonical finance facts + published Tax Simulation results + opening balance
                    |                         |
                    +------------+------------+
                                 v
                     [Eligibility / Cutoff Gate]
                                 |
                    +------------+-------------+
                    |                          |
                    v                          v
       [Deterministic Baseline]       [Promoted Forecast Model]
                    |                  MLflow + backtest gate
                    +------------+-------------+
                                 v
                    [Daily Cash-Flow Calendar]
                                 |
                 +---------------+----------------+
                 |               |                |
                 v               v                v
           [Current]       [Transition]      [Split]
                 |               |                |
                 +---------------+----------------+
                                 v
                      [Versioned Stress Engine]
                                 |
             +-------------------+-------------------+
             v                   v                   v
       [Float Delta]      [Liquidity/Gap]     [Driver Evidence]
             |                                       |
             +-------------------+-------------------+
                                 v
                    [Immutable Digital Twin Gold]
                                 |
                      [Query API / Control Tower]
```

The pipeline is analytical and tenant-scoped. It consumes only closed canonical batches and immutable Wave 3 simulations. A pure Python `Decimal` reference engine provides deterministic local behavior; Databricks implements the same contract at scale. Forecasting is optional: an unpromoted or failing model automatically falls back to the governed deterministic baseline.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Digital Twin Contract | Daily grain, scenarios, indicators, explanations and lineage | ODCS YAML |
| Scenario Policy | Horizons, eligibility, liquidity floor and stress parameters | Versioned YAML |
| Reference Cash Engine | Deterministic daily ledger and working-capital calculation | Python `Decimal` |
| Eligibility Gate | Verify opening balance, history, completeness and published tax inputs | Python/PySpark |
| Baseline Forecaster | Repeatable seasonal/rolling baseline with no ML dependency | Python/PySpark |
| Forecast Adapter | Load only MLflow models promoted through backtest/governance | Python + MLflow |
| Backtest Evaluator | MAPE, bias and interval coverage by horizon | Python/PySpark |
| Stress Engine | Independent and combined shocks with marginal driver attribution | Python/PySpark |
| Digital Twin Gold | Append-only daily projections, summaries and evidence | Databricks, Delta |
| Projection Repository | Tenant/CNPJ latest/history/comparison reads | Python protocol/in-memory wave adapter |
| Query API | Projection, cash curve, comparison and evidence endpoints | FastAPI |
| Control Tower | Cash curve, gap, float loss, stress and source links | Next.js, TypeScript |

---

## Key Decisions

### Decision 1: Deterministic baseline is always the safety floor

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Many CNPJs will not have sufficient history for a reliable statistical forecast, but cash arithmetic and explicit scenario assumptions remain useful.

**Choice:** Always produce a deterministic baseline when eligibility for cash projection is met. A statistical model may replace only the forecast component after passing versioned backtest thresholds; otherwise the result declares `model_mode: deterministic_baseline`.

**Rationale:** The platform remains useful and reproducible without presenting an unvalidated model as financial truth.

**Alternatives Rejected:**
1. Require ML for every projection - rejected because sparse histories would block the product.
2. Use an unvalidated model and add a disclaimer - rejected because disclaimer does not control model risk.
3. Generate projections with an LLM - rejected because monetary time series require deterministic numeric methods.

**Consequences:**
- Baseline and promoted models share the same output contract.
- Model failure degrades safely instead of failing the entire twin.
- UI displays model mode and backtest metrics.

---

### Decision 2: Daily immutable ledger is the primary grain

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Working-capital gaps depend on timing; monthly aggregates can hide intra-month negative cash.

**Choice:** Persist one row per tenant, CNPJ, projection, scenario and calendar day, plus immutable projection summary and evidence datasets.

**Rationale:** Daily grain supports running balances, payment delays, split timing and exact minimum-cash dates while remaining tractable at the wave scale.

**Alternatives Rejected:**
1. Monthly grain - rejected because it masks timing risk.
2. Transaction-level Gold only - rejected because query and scenario comparison become unnecessarily expensive.

**Consequences:**
- A generated calendar fills zero-movement dates.
- Running totals use ordered Spark windows and deterministic Decimal arithmetic.

---

### Decision 3: Stress assumptions are configuration, never hidden model state

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Users must distinguish model behavior from deliberate business shocks.

**Choice:** Store stress scenarios in versioned YAML with explicit driver, operation, magnitude, applicable period and approval metadata. Overrides create a new assumption snapshot and require actor/justification.

**Rationale:** Enables replay, marginal attribution and audit without retraining a model.

**Alternatives Rejected:**
1. Hardcode shocks in notebooks - rejected because changes are invisible and unreproducible.
2. Let models infer all shocks - rejected because scenario intent would not be auditable.

**Consequences:**
- Every result references `assumption_version` and checksum.
- Combined scenarios apply drivers in a documented stable order.

---

### Decision 4: Tax provenance is inherited, not duplicated

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Digital Twin indicators depend on Wave 3 tax results and must show official links without creating another rule catalog.

**Choice:** Store Wave 3 `simulation_id`, `rule_id` and `source_id` lineage in projection evidence. Query responses resolve the immutable source metadata from the simulation result.

**Rationale:** Preserves one calculation authority and prevents legal-source drift.

**Alternatives Rejected:**
1. Copy legal documents into the twin - rejected because duplicated provenance can diverge.
2. Recalculate taxes inside the twin - rejected because it creates a second Tax Engine.

**Consequences:**
- Missing published simulation lineage blocks official tax-affected indicators.
- Non-tax financial assumptions cite internal evidence rather than an artificial legal source.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `contracts/data/digital-twin-projection.contract.yaml` | Create | ODCS daily projection, summary, model and lineage contract | @data-contracts-engineer | None |
| 2 | `config/digital-twin-scenarios.yaml` | Create | Horizons, eligibility, cash floor and governed stress scenarios | @business-analyst | None |
| 3 | `data/databricks/resources/digital_twin.yml` | Create | Databricks pipeline/job and MLflow configuration | @databricks-spark-expert | 1, 2 |
| 4 | `data/databricks/src/digital_twin_config.py` | Create | Strict scenario/eligibility loader and checksum | @python-developer | 2 |
| 5 | `data/databricks/src/digital_twin_reference.py` | Create | Pure Decimal daily ledger, stress and indicator oracle | @python-developer | 2, 4 |
| 6 | `data/databricks/src/digital_twin_forecast.py` | Create | Deterministic baseline, model adapter and fallback policy | @ai-data-engineer | 2, 4 |
| 7 | `data/databricks/src/digital_twin_backtest.py` | Create | MAPE, bias, interval coverage and promotion decision | @ai-data-engineer | 6 |
| 8 | `data/databricks/src/gold_digital_twin.py` | Modify | Eligibility, daily projection, stresses, evidence and append-only Gold | @databricks-spark-expert | 1-7 |
| 9 | `services/query-service/src/taxflow_query/digital_twin.py` | Create | Pydantic models, Decimal invariants and comparisons | @python-developer | 1 |
| 10 | `services/query-service/src/taxflow_query/digital_twin_repository.py` | Create | Append-only tenant/CNPJ projection repository | @python-developer | 9 |
| 11 | `services/query-service/src/taxflow_query/api.py` | Modify | Latest/history/curve/comparison endpoints | @python-developer | 9, 10 |
| 12 | `contracts/api/openapi.yaml` | Modify | Digital Twin response and evidence schemas | (general) | 1, 11 |
| 13 | `apps/control-tower/src/app/digital-twin/page.tsx` | Create | Cash curve, float, gap, stresses, model mode and citations | @ecc-typescript-reviewer | 12 |
| 14 | `tests/digital_twin/test_cash_engine.py` | Create | Ledger, running balance, float and gap unit tests | @test-generator | 5 |
| 15 | `tests/digital_twin/test_stress_scenarios.py` | Create | Six independent and three combined stress tests | @test-generator | 2, 5 |
| 16 | `tests/digital_twin/test_backtest.py` | Create | Metrics, promotion and deterministic fallback | @test-generator | 6, 7 |
| 17 | `tests/digital_twin/test_digital_twin_api.py` | Create | Tenant isolation, history, comparison and citation API tests | @test-generator | 9-12 |
| 18 | `tests/digital_twin/test_digital_twin_parity.py` | Create | Reference/Spark-compatible semantic parity | @test-generator | 5, 8 |
| 19 | `tests/digital_twin/test_digital_twin_performance.py` | Create | 100k deterministic workload gate | @test-generator | 5, 8 |
| 20 | `.github/workflows/ci.yml` | Modify | Digital Twin contract, unit, backtest, parity and performance gates | @ci-cd-specialist | 14-19 |

**Total Files:** 20

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @data-contracts-engineer | 1 | ODCS data product, quality and lineage |
| @business-analyst | 2 | Financial scenarios, assumptions and measurable drivers |
| @databricks-spark-expert | 3, 8 | Spark windows, Delta tables, performance and DLT quality |
| @python-developer | 4, 5, 9-11 | Typed deterministic domain/API implementation |
| @ai-data-engineer | 6, 7 | Forecast lifecycle, backtest and MLflow promotion |
| @ecc-typescript-reviewer | 13 | Typed Next.js data visualization and citations |
| @test-generator | 14-19 | Unit, scenario, model, API, parity and load tests |
| @ci-cd-specialist | 20 | Hosted test and workspace gates |
| (general) | 12 | Existing OpenAPI conventions are sufficient; no dedicated API agent was discovered |

**Agent Discovery:**
- Scanned: `${CLAUDE_PLUGIN_ROOT}/agents/**/*.md`
- Matched by: contract, finance, Python, Spark/Databricks, ML, TypeScript, testing and CI keywords
- Confidence: 0.95 for contract/Spark/testing; 0.85 for finance-specific implementation

---

## Code Patterns

### Pattern 1: Decimal daily cash ledger

```python
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class DailyCash:
    projection_date: date
    opening_cash: Decimal
    inflow: Decimal
    outflow: Decimal
    tax_split_outflow: Decimal
    closing_cash: Decimal


def project_day(day: date, opening: Decimal, inflow: Decimal,
                outflow: Decimal, tax_split: Decimal) -> DailyCash:
    closing = opening + inflow - outflow - tax_split
    return DailyCash(day, opening, inflow, outflow, tax_split, closing)
```

Each following day receives exactly the prior `closing_cash`; no runtime clock or binary float enters the formula.

### Pattern 2: Working-capital indicators

```python
from decimal import Decimal


def liquidity_indicators(closing_cash: tuple[Decimal, ...],
                         minimum_cash: Decimal) -> dict[str, Decimal | int]:
    gaps = tuple(max(Decimal("0"), minimum_cash - value) for value in closing_cash)
    return {
        "minimum_balance": min(closing_cash),
        "maximum_working_capital_gap": max(gaps),
        "days_below_minimum": sum(value < minimum_cash for value in closing_cash),
    }
```

### Pattern 3: Backtest promotion with safe fallback

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class BacktestMetrics:
    mape: Decimal
    absolute_bias: Decimal
    coverage: Decimal


def can_promote(metrics: BacktestMetrics, maximum_mape: Decimal) -> bool:
    return (
        metrics.mape <= maximum_mape
        and metrics.absolute_bias <= Decimal("0.05")
        and metrics.coverage >= Decimal("0.80")
    )
```

If `can_promote` is false or the model artifact is unavailable, execution selects the deterministic baseline and records the reason.

### Pattern 4: Configuration structure

```yaml
digital_twin:
  version: 1.0.0
  horizons_days: [30, 90, 180, 365]
  minimum_history_days: 90
  minimum_cash:
    mode: fixed
    amount: "100000.00"
  model_gate:
    maximum_mape: "0.15"
    maximum_absolute_bias: "0.05"
    minimum_interval_coverage: "0.80"
  stresses:
    - id: revenue_down_10
      driver: revenue
      operation: multiply
      factor: "0.90"
```

---

## Data Flow

```text
1. Closed canonical finance batch and published tax simulations arrive
   |
   v
2. Tenant/CNPJ, cutoff, completeness and lineage eligibility are validated
   |
   v
3. Daily expected movements are generated with deterministic baseline
   |
   v
4. A promoted model may replace only forecasted movement estimates
   |
   v
5. Current, transition and split ledgers are calculated day by day
   |
   v
6. Versioned independent/combined stresses are applied
   |
   v
7. Float delta, minimum balance, days below floor and maximum gap are derived
   |
   v
8. Projection, summary, explanations, tax links and audit metadata are appended
   |
   v
9. Tenant-scoped API and Control Tower expose curves and comparisons
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Wave 3 Tax Simulation Gold | Delta immutable snapshot | Unity Catalog workload identity |
| Canonical Silver finance facts | Delta table | Unity Catalog ABAC/RBAC |
| MLflow Model Registry | Versioned model/artifact lookup | Databricks workload identity |
| Query API | Databricks SQL/repository adapter | Service identity + tenant claims |
| Control Tower | REST API | OIDC/JWT tenant claims |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Decimal ledger, float and liquidity indicators | 14 | pytest | 100% formulas/boundaries |
| Scenario | Independent/combined shocks and attribution | 15 | pytest parametrization | 6 independent + 3 combined |
| Model | Backtest metrics, promotion and fallback | 16 | pytest | 100% gate branches |
| API/Security | Latest/history/curve/comparison/tenant denial | 17 | FastAPI TestClient | All endpoints and negative cases |
| Parity | Reference versus Spark-compatible output | 18 | pytest + Decimal | Exact daily values/IDs |
| Performance | 100k operations | 19 | pytest + Databricks job | Local reference gate + <=15 min workspace |
| E2E | Closed batch to Control Tower | Hosted CI/workspace | Automated API/UI check | DT-AT-001 through DT-AT-014 |

Acceptance coverage:

| Acceptance IDs | Evidence |
|----------------|----------|
| DT-AT-001,002,008,009 | 14, 17, 18 |
| DT-AT-003,004,005,006,013 | 15, 17 |
| DT-AT-007 | 4, 8, 17 |
| DT-AT-010,011 | 17 |
| DT-AT-012 | 16 |
| DT-AT-014 | 19 + workspace run |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Missing opening balance/history | Publish structured ineligibility, not official projection | After data correction |
| Missing Wave 3 lineage | Block tax-affected official indicators | After lineage correction |
| Invalid assumption version | Reject execution before calculation | No |
| Model absent or gate failed | Fall back to deterministic baseline and record reason | No model retry |
| Invalid monetary value | Quarantine input with reason | After correction |
| Duplicate fingerprint | Return existing immutable projection | Safe return |
| Tenant/CNPJ unauthorized | Deny without disclosure and audit | No |
| Transient Databricks/storage failure | Retry idempotently with bounded backoff | Yes |
| Parity or reconciliation failure | Block Gold publication and release | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `digital_twin.version` | semver | none | Assumption policy version |
| `digital_twin.horizons_days` | integer list | `30,90,180,365` | Supported horizons |
| `digital_twin.minimum_history_days` | integer | `90` | Statistical model eligibility |
| `digital_twin.minimum_cash.amount` | decimal string | profile-specific | Liquidity floor |
| `digital_twin.model_gate.maximum_mape` | decimal string | `0.15` | Promotion threshold |
| `digital_twin.model_gate.maximum_absolute_bias` | decimal string | `0.05` | Bias threshold |
| `digital_twin.model_gate.minimum_interval_coverage` | decimal string | `0.80` | Forecast coverage gate |
| `digital_twin.random_seed` | integer | `360` | Reproducible model operations |

---

## Security Considerations

- Filter tenant/CNPJ before joining, aggregating, training or scoring.
- Never train a cross-tenant model in this wave.
- Tokenize protected tax IDs in analytics and expose only authorized values through the API.
- Record every assumption override with actor, justification and before/after values.
- Do not use projections for automated credit decisions or execute financial transactions.
- Keep model artifacts, training windows, metrics and promotion actors immutable/auditable.
- Resolve official tax links only from immutable Wave 3 results; never accept arbitrary URLs.
- Avoid sensitive values in logs, metrics and model tags.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured projection/scenario/model IDs, tenant token and cutoff; no raw financial payload |
| Metrics | Eligibility, pipeline latency, MAPE, bias, coverage, fallback rate, gap severity and parity failures |
| Tracing | OpenTelemetry/API correlation plus Databricks job/run and MLflow run IDs |
| Audit | Append-only execution, model promotion, assumption override, query and denial events |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Silver Finance Facts] --------+
                                +--> [Eligibility] --> [Daily Baseline] ----+
[Tax Simulation Gold] ---------+          |                               |
                                          v                               v
                                   [Ineligible]                 [Optional ML Forecast]
                                                                          |
[Scenario Policy] --> [Validate/Freeze] ----------------------------------+
                                                                          v
                                                                  [Stress Engine]
                                                                          |
                                                                          v
                                                               [Reconciliation Gate]
                                                                  |             |
                                                                fail          pass
                                                                  v             v
                                                           [Quarantine] [Twin Gold]
                                                                                |
                                                                          [API / UI]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|-------------|-------------|-----------|
| `gold_digital_twin_daily` | `tenant_id`, `projection_month` | tenant/month; cluster CNPJ/scenario/date | Time-range and tenant pruning |
| `gold_digital_twin_summary` | liquid cluster `tenant_id`, `company_tax_id` | one projection/scenario | Latest/history comparison |
| `gold_digital_twin_evidence` | liquid cluster `projection_id` | one driver/evidence row | Explanation reconstruction |
| `digital_twin_backtest` | `model_version`, `horizon_days` | model/horizon | Promotion and drift review |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Finance facts | closed-batch append/dedup | `event_id`, `input_hash` | Current corrected batch |
| Tax simulation input | immutable version reference | `simulation_id` | None |
| Daily projection | insert-only fingerprint | `projection_id`, `projection_date`, `scenario_id` | Retry same projection only |
| Latest summary | derived window/materialized view | `published_at` | Affected tenant/CNPJ |
| Backtest | append per model/window | `backtest_id` | New candidate only |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Add optional indicator/driver | Contract minor version, nullable field/evidence type | Consumers ignore new field |
| New scenario | New assumption version; no historical mutation | Reuse prior assumption snapshot |
| Model output change | New model/contract version and parallel validation | Keep promoted prior model |
| Decimal scale/type change | New major version and dual columns | Continue prior major output |
| Rename/remove | Deprecation window and compatibility view | Restore alias/view |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Identity/completeness | DLT expectations + contract tests | 0 missing tenant/CNPJ/date/version | Block/quarantine |
| Daily continuity | Spark calendar comparison | 100% days in horizon | Block projection |
| Cash reconciliation | Decimal invariant | opening + inflow - outflow - split = closing exactly | Block publication |
| Tax lineage | Contract join check | 100% tax effects linked to simulation/rule/source | Block publication |
| Scenario coverage | Config/test | >=6 independent and >=3 combined | Block config promotion |
| Model promotion | Backtest | MAPE<=15%, abs bias<=5%, coverage>=80% | Fall back to baseline |
| Parity | pytest/Spark comparison | 100% daily money and indicator equality | Block release |
| Freshness/performance | Job metrics | 100k <=15 minutes | Block wave acceptance |
| Tenant isolation | API/policy tests | 0 cross-tenant disclosures | Block/security incident |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | design-agent | Initial Wave 4 design with deterministic baseline, governed forecast, stress engine and inherited tax provenance |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_DIGITAL_TWIN_TAXFLOW_360.md`
