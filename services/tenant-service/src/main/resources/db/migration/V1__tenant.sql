CREATE TABLE tenant (
  id UUID PRIMARY KEY, legal_name VARCHAR(200) NOT NULL, company_tax_id VARCHAR(14) NOT NULL UNIQUE,
  active BOOLEAN NOT NULL DEFAULT TRUE, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE tenant_user_role (
  tenant_id UUID NOT NULL REFERENCES tenant(id), user_id UUID NOT NULL, role VARCHAR(32) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (tenant_id, user_id, role)
);
CREATE INDEX tenant_user_role_tenant_idx ON tenant_user_role(tenant_id);

ALTER TABLE tenant ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON tenant
  USING (id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID)
  WITH CHECK (id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);

ALTER TABLE tenant_user_role ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_user_role FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_user_role_isolation ON tenant_user_role
  USING (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID);
