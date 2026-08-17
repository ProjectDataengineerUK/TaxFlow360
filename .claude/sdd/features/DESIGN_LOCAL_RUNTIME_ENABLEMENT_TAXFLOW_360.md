# DESIGN: Habilitação dos Runtimes Locais TaxFlow 360

> Technical design for implementing Habilitação dos Runtimes Locais TaxFlow 360

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360 |
| **Date** | 2026-08-17 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360.md](./DEFINE_LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360.md) |
| **Status** | Ready for Build |
| **Design Confidence** | 0.95 — CI/testing/security patterns and toolchain specialists found |

---

## Architecture Overview

```text
[.tool-versions + approved source manifest]
                    |
             [PowerShell bootstrap]
    download -> SHA-256 -> extract to user tool cache
                    |
             [Session environment]
  JAVA_HOME / PATH / TF / Databricks / Node 22
                    |
              [Preflight detector]
  expected version + path + checksum + capability
           /           |             \
        PASS          FAIL          BLOCKED
           \           |             /
                [Local gate runner]
 Python | JVM services | npm ci/typecheck/build | Terraform offline | CLI version
                         |
           [Content-addressed local evidence]
                         |
           [Certification matrix local gates only]
```

Tool binaries live in a user-controlled cache outside the repository. Repository scripts contain only manifests, verification and orchestration. Environment changes apply to the current PowerShell process unless the user explicitly requests persistence.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Source manifest | Exact version, official HTTPS URL, archive/JAR SHA-256 and executable path | Approved YAML |
| Bootstrap | Download, verify, extract and reject mismatches | PowerShell 7/Windows PowerShell |
| Session activator | Set task-specific variables and prepend verified binaries to PATH | PowerShell |
| Preflight | Inspect binaries, versions, paths, locks and forbidden credentials | Python/Pydantic |
| Gate runner | Execute bounded Python/JVM/frontend/Terraform/Databricks-local gates | Python subprocess |
| Evidence writer | Redact output, hash evidence and emit certification-compatible JSON | Existing certification package |
| Runtime report | Summarize PASS/FAIL/BLOCKED and unresolved hosted gates | Markdown/JSON |

---

## Key Decisions

### Decision 1: Portable user cache and session-only activation

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** The machine already contains Node 20 and other tools may be used by unrelated projects. System-wide installers and permanent PATH edits can break existing workflows or require administrator authority.

**Choice:** Store verified archives under a task-specific user cache outside Git and activate them by prepending paths only in the current PowerShell process. Do not uninstall or overwrite existing tools. Administrative/system-wide installation requires a separate explicit approval.

**Rationale:** This is reversible, preserves existing state and makes the exact tool selected by a test visible. Removing the cache or closing the session restores the prior environment.

**Alternatives Rejected:**
1. Replace system Node/Java — rejected because it can disrupt other projects.
2. Commit binaries into the repository — rejected due to size, supply-chain and portability issues.
3. Persist global PATH automatically — rejected because it creates hidden machine-wide state.

**Consequences:**
- Each new shell must run the activation script.
- Hosted CI remains canonical for release certification even after local gates pass.

---

### Decision 2: Manifest-driven downloads with fail-closed integrity

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Tool downloads are executable supply-chain inputs. Version output alone does not prove their origin or integrity.

**Choice:** Every downloadable artifact requires exact official URL, SHA-256, archive layout and executable/version expectation in an approved manifest. Bootstrap downloads to a temporary file, hashes before extraction, rejects redirects to non-approved final hosts where observable and never executes an unverified artifact.

**Rationale:** A declarative manifest supports review, repeatability and evidence. Fail-closed behavior prevents a network or checksum problem from silently substituting a different version.

**Alternatives Rejected:**
1. `latest` download URLs — rejected because builds become non-reproducible.
2. Trust TLS without checksum — rejected because it does not bind expected release bytes.
3. Package-manager install without version/evidence — rejected because resolution may drift.

**Consequences:**
- Checksums must be sourced and reviewed when versions change.
- If an official artifact cannot be downloaded, the corresponding gate stays BLOCKED.

---

### Decision 3: Wrapper JAR is restored, verified and not handcrafted

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Wrapper scripts exist, but Gradle cannot run without the binary wrapper JAR. Binary content cannot be safely recreated through a text patch.

**Choice:** Download the official Gradle 8.12.1 wrapper JAR, verify expected SHA-256 `2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046`, then place it at `gradle/wrapper/gradle-wrapper.jar`. The Gradle distribution retains its independent SHA-256 check.

**Rationale:** The official binary and two-layer verification are the standard reproducible boundary. Any mismatch blocks execution.

**Alternatives Rejected:**
1. Generate a fake/minimal JAR — rejected because it is unauditable and unsafe.
2. Depend permanently on global Gradle — rejected because wrapper consistency would remain unresolved.

**Consequences:**
- Build requires approved network access once.
- Wrapper JAR checksum is recorded in preflight evidence.

---

### Decision 4: Local Terraform is offline-safe and cannot apply

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-17 |

**Context:** Installing Terraform should not imply cloud authority. Provider initialization may require network, while plan/apply require credentials and may change state.

**Choice:** Local runner exposes only `fmt -check`, structural tests and `validate` where providers are available. It rejects commands containing `apply`, `destroy`, `import` or credential/profile inputs. Provider/cloud plan gates remain hosted BLOCKED.

**Rationale:** Toolchain enablement and infrastructure authorization are separate boundaries.

**Alternatives Rejected:**
1. Run plan with dummy credentials — rejected because results are misleading.
2. Auto-configure cloud profiles — rejected because credentials are out of scope.

**Consequences:**
- Some validate/test work may wait for provider cache/network.
- Passing local Terraform does not certify any cloud adapter runtime.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `config/local-toolchains.yaml` | Create | Official URLs, SHA-256, layouts and expected versions | @data-governance-auditor | `.tool-versions` |
| 2 | `tools/preflight/pyproject.toml` | Create | Self-contained preflight package | @python-developer | None |
| 3 | `tools/preflight/src/taxflow_preflight/models.py` | Create | Tool/gate/evidence types | @python-developer | 1,2 |
| 4 | `tools/preflight/src/taxflow_preflight/detect.py` | Create | Windows command/path/version/checksum detection | @python-developer | 3 |
| 5 | `tools/preflight/src/taxflow_preflight/gates.py` | Create | Bounded local gate runner and prohibited-command checks | @ecc-security-reviewer | 3,4 |
| 6 | `tools/preflight/src/taxflow_preflight/cli.py` | Create | `detect`, `run`, `report` commands | @python-developer | 3-5 |
| 7 | `tools/preflight/bootstrap-toolchains.ps1` | Create | Approved download/hash/extract bootstrap | @shell-script-specialist | 1 |
| 8 | `tools/preflight/activate-toolchains.ps1` | Create | Session-only environment activation | @shell-script-specialist | 1,7 |
| 9 | `tests/preflight/test_manifest.py` | Create | Four-eyes, URLs, checksums and exact version tests | @test-generator | 1-4 |
| 10 | `tests/preflight/test_gates.py` | Create | Missing/mismatch/PASS and forbidden Terraform commands | @ecc-security-reviewer | 3-6 |
| 11 | `docs/runbooks/local-toolchains.md` | Create | Approval, install, activation, rollback and troubleshooting | @code-documenter | 1,7,8 |
| 12 | `.claude/sdd/reports/LOCAL_RUNTIME_REPORT_TEMPLATE.md` | Create | Version/path/checksum/gate evidence template | @data-governance-auditor | 3,6 |

**Total Files:** 12

The Build may create `gradle/wrapper/gradle-wrapper.jar` only after approved download and checksum verification. It is a verified binary artifact, not source generated by an agent.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @data-governance-auditor | 1,12 | Approved supply-chain manifest and evidence |
| @python-developer | 2-4,6 | Typed portable preflight CLI |
| @ecc-security-reviewer | 5,10 | Command allowlist and adversarial tests |
| @shell-script-specialist | 7,8 | Safe PowerShell download/session handling |
| @test-generator | 9 | Deterministic manifest tests |
| @code-documenter | 11 | Reversible operator workflow |

**Agent Discovery:**
- Scanned: `.claude/agents/**/*.md`
- Matched by: PowerShell, Python, security, testing and governance capabilities

---

## Code Patterns

### Pattern 1: Fail-closed SHA-256 verification

```powershell
$actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
if ($actual -ne $expectedSha256.ToLowerInvariant()) {
    throw "Checksum mismatch for $toolName"
}
```

### Pattern 2: Session-only activation

```powershell
$toolBin = [System.IO.Path]::GetFullPath($verifiedBinDirectory)
$env:PATH = "$toolBin$([System.IO.Path]::PathSeparator)$env:PATH"
```

### Pattern 3: Configuration Structure

```yaml
version: 1.0.0
status: approved
cacheRootVariable: TAXFLOW_TOOL_CACHE
tools:
  - id: terraform
    version: 1.10.5
    officialHosts: [releases.hashicorp.com]
    archiveUrl: https://releases.hashicorp.com/terraform/1.10.5/terraform_1.10.5_windows_amd64.zip
    sha256: <official-lowercase-64-hex>
    executable: terraform.exe
    versionPattern: '^Terraform v1\.10\.5$'
approval:
  preparedBy: platform-toolchain-a
  approvedBy: platform-toolchain-b
```

### Pattern 4: Command allowlist

```python
ALLOWED_TERRAFORM = {"version", "fmt", "validate", "test"}

def validate_terraform_args(args: tuple[str, ...]) -> None:
    if not args or args[0] not in ALLOWED_TERRAFORM:
        raise PermissionError("Terraform command is outside local enablement scope")
```

---

## Data Flow

```text
1. Preflight reads expected tools and observes current PATH without mutation.
2. User approves each missing external download when required.
3. Bootstrap downloads to temp, verifies hash, extracts to user cache.
4. Activation configures only the current PowerShell process.
5. Preflight rechecks executable, version, path and artifact checksum.
6. Gate runner executes Python, JVM, frontend and safe Terraform/CLI checks.
7. Outputs are redacted, hashed and mapped to PASS/FAIL/BLOCKED.
8. Local report updates only executed gates; hosted/human gates stay BLOCKED.
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Eclipse Adoptium | Official Temurin archive/API | Public HTTPS; no credential |
| Gradle distributions | Official ZIP/wrapper JAR | Public HTTPS + SHA-256 |
| Node.js distributions | Official Windows archive | Public HTTPS + SHASUMS256 |
| HashiCorp releases | Official Terraform ZIP | Public HTTPS + SHA-256 |
| Databricks CLI releases | Official release artifact | Public HTTPS + SHA-256 |
| npm registry | `npm ci` from committed lock | Public HTTPS; no project secret |

No cloud API or Databricks workspace is contacted by this feature.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | Manifest, version parsing, checksum and command allowlist | 9,10 | pytest | LR-AT-001-003,005,008,009,011-013 |
| Integration | Portable cache, activation and preflight subprocess | 7-10 | PowerShell + pytest | Exact selected paths/versions |
| JVM | All Kotlin services | gate runner | Gradle/JUnit | LR-AT-004 |
| Frontend | Lock unchanged, typecheck and build | gate runner | npm/Next/TypeScript | LR-AT-006,007 |
| Python | Full regression | gate runner | pytest | LR-AT-010 |
| Evidence | Redaction, hashes and report completeness | 3,5,6,12 | pytest | LR-AT-014 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Approval/network unavailable | Do not download; record BLOCKED | After approval/network change |
| URL/host not allowlisted | Reject before request | No |
| SHA-256 mismatch | Delete temporary artifact, record FAIL and alert | No blind retry |
| Archive traversal/invalid layout | Reject extraction and remove staging directory | No |
| Version mismatch | Keep binary quarantined/unselected; FAIL | After correct artifact |
| Build/test failure | Preserve redacted evidence and mark FAIL | After code/config fix |
| npm lock changes | Fail reproducibility gate and restore only by reviewed patch | No automatic mutation |
| Terraform prohibited command | Reject before subprocess and audit | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `TAXFLOW_TOOL_CACHE` | absolute path | user-local task cache | Portable tool root; outside Git |
| `downloadTimeoutSeconds` | integer | `120` | Bounded download time |
| `maxArchiveBytes` | integer | per tool | Download size ceiling |
| `sessionOnly` | boolean | `true` | Prohibit persistent PATH mutation |
| `verifySha256` | boolean | `true` | Cannot be disabled |
| `allowedTerraformCommands` | list | version/fmt/validate/test | Local boundary |
| `evidenceDirectory` | path | `.local-evidence/runtime` | Gitignored outputs |

---

## Security Considerations

- Downloads use exact official HTTPS hosts/paths, fixed versions, size limits and SHA-256 before extraction/execution.
- ZIP entries are checked against path traversal; symlinks/reparse points and unexpected executables are rejected.
- Temporary and cache targets resolve outside the repository and never use broad home/workspace deletion.
- Scripts do not request/store cloud credentials, tokens or permanent environment variables.
- Terraform commands are allowlisted and no `apply`, `destroy`, `import`, saved credentials or profiles are accepted.
- Evidence is redacted before hashing; user paths may be normalized and secrets cause failure.
- Existing Node 20/Docker/Python installations are preserved; rollback closes the session and removes only validated task-cache targets.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured tool/download/checksum/path/version/gate events with URLs and user paths redacted as needed |
| Metrics | Download duration/bytes, detection status, gate duration and PASS/FAIL/BLOCKED counts |
| Tracing | Run ID connects bootstrap, detection, command and evidence hash |
| Audit | Approved manifest checksum, official origin, artifact SHA-256 and executed command argv |

---

## Pipeline Architecture (if applicable)

### DAG Diagram

```text
[Expected manifest] -> [Detect] -> missing/mismatch -> [Approved bootstrap]
                           |                              |
                           +---------- [Activate] <-------+
                                          |
             +----------------------------+-------------------------+
             |             |              |            |            |
          [Python]        [JVM]        [Frontend]   [Terraform] [DBX version]
             \             |              |            |            /
                       [Redact + hash evidence]
                                  |
                       [Local runtime report]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| Local evidence files | `run_id` directory | per run | Isolate attempts and simplify cleanup |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Tool cache | Reuse only exact version+SHA artifact | `tool/version/sha256` | none |
| Preflight | New immutable observation per run | `run_id,tool` | current run |
| Gate evidence | Append attempt | `run_id,gate,attempt` | current run |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| Tool version | Reviewed manifest/lock update with new checksum | Select prior cache/version |
| New tool | Add manifest entry and detection adapter | Disable unrequired entry |
| Evidence field | Optional minor contract addition | Ignore field |
| Status semantic change | Major contract version; preserve prior reports | Prior preflight package |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Manifest four-eyes | pytest | distinct actors | Block bootstrap |
| Official origin | URL validator | 100% allowlisted | Block download |
| Artifact integrity | SHA-256 | 100% exact | Delete temp/FAIL |
| Expected version/path | preflight | 100% exact | BLOCKED/FAIL |
| npm lock unchanged | Git diff/hash | exact | FAIL frontend gate |
| Prohibited operations | command validator | 0 calls | Security FAIL |
| Evidence completeness | report validator | all tools/gates explicit | Missing → BLOCKED |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-17 | design-agent | Portable Windows toolchain architecture and 12-file manifest |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_LOCAL_RUNTIME_ENABLEMENT_TAXFLOW_360.md`
