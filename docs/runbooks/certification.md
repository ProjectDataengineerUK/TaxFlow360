# Certification runbook

Certification is synthetic-only and produces a release candidate, not a production deployment.

1. Pin the candidate commit, logical cutoff, toolchain and gate-registry checksum.
2. Obtain protected-environment approval, workload identities, regions and budgets.
3. Run `ci-fast`; store JUnit/SARIF/build evidence by SHA-256.
4. Dispatch `certification-hosted` for the same candidate. Cloud jobs are plan-only by default.
5. Capture Databricks bundle, CDF/stream progress, AI Search and MLflow evaluation evidence.
6. Run E2E, tenancy, parity, provenance, security, recovery and performance gates.
7. Obtain independent tax catalog, regulatory corpus and security approvals.
8. Evaluate the complete matrix. Missing evidence is `BLOCKED`.
9. Create signed RC artifacts only after `APPROVED_FOR_RC`.
10. Verify every ephemeral environment is destroyed; a teardown failure blocks closure.

Never put credentials in configuration/evidence, run with real taxpayer data, broaden targets during teardown, or infer PASS from an unavailable runtime.
