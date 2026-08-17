CREATE TABLE regulatory_change_request(
 tenant_id uuid NOT NULL, change_request_id uuid NOT NULL, version bigint NOT NULL CHECK(version>0),
 status text NOT NULL, payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(tenant_id,change_request_id,version));
CREATE TABLE regulatory_audit(
 id uuid PRIMARY KEY,tenant_id uuid NOT NULL,actor_id text NOT NULL,action text NOT NULL,
 payload_sha256 char(64) NOT NULL,occurred_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE regulatory_outbox(
 id uuid PRIMARY KEY,tenant_id uuid NOT NULL,aggregate_id uuid NOT NULL,event_type text NOT NULL,
 payload jsonb NOT NULL,occurred_at timestamptz NOT NULL DEFAULT now(),published_at timestamptz);
ALTER TABLE regulatory_change_request ENABLE ROW LEVEL SECURITY; ALTER TABLE regulatory_change_request FORCE ROW LEVEL SECURITY;
ALTER TABLE regulatory_audit ENABLE ROW LEVEL SECURITY; ALTER TABLE regulatory_audit FORCE ROW LEVEL SECURITY;
ALTER TABLE regulatory_outbox ENABLE ROW LEVEL SECURITY; ALTER TABLE regulatory_outbox FORCE ROW LEVEL SECURITY;
CREATE POLICY change_tenant ON regulatory_change_request USING(tenant_id=current_setting('app.tenant_id',true)::uuid) WITH CHECK(tenant_id=current_setting('app.tenant_id',true)::uuid);
CREATE POLICY audit_tenant ON regulatory_audit USING(tenant_id=current_setting('app.tenant_id',true)::uuid) WITH CHECK(tenant_id=current_setting('app.tenant_id',true)::uuid);
CREATE POLICY outbox_tenant ON regulatory_outbox USING(tenant_id=current_setting('app.tenant_id',true)::uuid) WITH CHECK(tenant_id=current_setting('app.tenant_id',true)::uuid);
CREATE INDEX regulatory_outbox_pending ON regulatory_outbox(occurred_at) WHERE published_at IS NULL;
