CREATE TABLE reconciliation_result (
 id uuid NOT NULL, tenant_id uuid NOT NULL, company_tax_id text NOT NULL,
 version bigint NOT NULL CHECK(version>0), fingerprint char(64) NOT NULL,
 status text NOT NULL, payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,id,version), UNIQUE(tenant_id,fingerprint));
CREATE TABLE reconciliation_review (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL, result_id uuid NOT NULL,
 actor_id uuid NOT NULL, previous_status text NOT NULL, current_status text NOT NULL,
 justification text NOT NULL CHECK(length(trim(justification))>0), evidence_ids jsonb NOT NULL,
 decided_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE reconciliation_outbox (
 id uuid PRIMARY KEY, tenant_id uuid NOT NULL, aggregate_id uuid NOT NULL,
 event_type text NOT NULL, payload jsonb NOT NULL, occurred_at timestamptz NOT NULL DEFAULT now(), published_at timestamptz);
ALTER TABLE reconciliation_result ENABLE ROW LEVEL SECURITY; ALTER TABLE reconciliation_result FORCE ROW LEVEL SECURITY;
ALTER TABLE reconciliation_review ENABLE ROW LEVEL SECURITY; ALTER TABLE reconciliation_review FORCE ROW LEVEL SECURITY;
ALTER TABLE reconciliation_outbox ENABLE ROW LEVEL SECURITY; ALTER TABLE reconciliation_outbox FORCE ROW LEVEL SECURITY;
CREATE POLICY reconciliation_tenant ON reconciliation_result USING (tenant_id=current_setting('app.tenant_id',true)::uuid) WITH CHECK (tenant_id=current_setting('app.tenant_id',true)::uuid);
CREATE POLICY review_tenant ON reconciliation_review USING (tenant_id=current_setting('app.tenant_id',true)::uuid) WITH CHECK (tenant_id=current_setting('app.tenant_id',true)::uuid);
CREATE POLICY outbox_tenant ON reconciliation_outbox USING (tenant_id=current_setting('app.tenant_id',true)::uuid) WITH CHECK (tenant_id=current_setting('app.tenant_id',true)::uuid);
CREATE INDEX reconciliation_outbox_pending ON reconciliation_outbox(occurred_at) WHERE published_at IS NULL;
