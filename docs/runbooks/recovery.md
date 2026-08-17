# Certification recovery runbook

- Stop new candidate runs and retain the exact run/candidate/state identifiers.
- For checkpoint failure, restore the approved checkpoint or replay immutable CDF range and compare semantic fingerprints.
- For PostgreSQL restore, use the staging backup, set tenant context, verify forced RLS and reconcile outbox IDs before consumers resume.
- For partial Terraform apply, use its saved state and approved plan; never delete a computed or broad target. Verify resource IDs belong to the certification run.
- For evidence mismatch, quarantine the object, mark the gate FAIL/BLOCKED and regenerate under a new attempt.
- Record measured RPO/RTO, actor, commands/tool versions, before/after checksums and residual resources.
