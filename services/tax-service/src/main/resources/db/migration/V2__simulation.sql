CREATE TABLE tax_legal_source (
    source_id UUID PRIMARY KEY,
    rule_id VARCHAR(100) NOT NULL,
    rule_version VARCHAR(32) NOT NULL,
    source_url TEXT NOT NULL CHECK (source_url LIKE 'https://%'),
    authority VARCHAR(200) NOT NULL,
    document_id VARCHAR(200) NOT NULL,
    provision VARCHAR(500) NOT NULL,
    published_on DATE NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL,
    content_sha256 CHAR(64) NOT NULL CHECK (content_sha256 ~ '^[a-f0-9]{64}$'),
    UNIQUE (rule_id, rule_version, document_id, provision),
    FOREIGN KEY (rule_id, rule_version) REFERENCES tax_rule(id, version)
);

CREATE TABLE tax_simulation (
    simulation_id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    transaction_id VARCHAR(100) NOT NULL,
    idempotency_key VARCHAR(200) NOT NULL,
    simulation_fingerprint CHAR(64) NOT NULL,
    rule_set_version VARCHAR(32) NOT NULL,
    effective_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tenant_id, idempotency_key),
    UNIQUE (tenant_id, simulation_fingerprint)
);

CREATE TABLE tax_simulation_scenario (
    simulation_id UUID NOT NULL REFERENCES tax_simulation(simulation_id),
    scenario VARCHAR(32) NOT NULL CHECK (scenario IN ('CURRENT', 'TRANSITION', 'CBS_IBS')),
    base_amount NUMERIC(20,2) NOT NULL CHECK (base_amount >= 0),
    tax_amount NUMERIC(20,2) NOT NULL CHECK (tax_amount >= 0),
    net_amount NUMERIC(20,2) NOT NULL,
    delta_from_current NUMERIC(20,2) NOT NULL,
    PRIMARY KEY (simulation_id, scenario)
);

CREATE TABLE tax_simulation_memory (
    simulation_id UUID NOT NULL REFERENCES tax_simulation(simulation_id),
    scenario VARCHAR(32) NOT NULL,
    line_no INTEGER NOT NULL CHECK (line_no >= 0),
    component VARCHAR(32) NOT NULL,
    expression TEXT NOT NULL,
    base_amount NUMERIC(20,2) NOT NULL,
    rate NUMERIC(12,10) NOT NULL,
    value NUMERIC(20,2) NOT NULL,
    rule_id VARCHAR(100) NOT NULL,
    rule_version VARCHAR(32) NOT NULL,
    PRIMARY KEY (simulation_id, scenario, line_no),
    FOREIGN KEY (simulation_id, scenario) REFERENCES tax_simulation_scenario(simulation_id, scenario)
);

ALTER TABLE tax_simulation ENABLE ROW LEVEL SECURITY;
ALTER TABLE tax_simulation FORCE ROW LEVEL SECURITY;
CREATE POLICY tax_simulation_tenant_policy ON tax_simulation
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);

ALTER TABLE tax_simulation_scenario ENABLE ROW LEVEL SECURITY;
ALTER TABLE tax_simulation_scenario FORCE ROW LEVEL SECURITY;
CREATE POLICY tax_simulation_scenario_tenant_policy ON tax_simulation_scenario
    USING (EXISTS (SELECT 1 FROM tax_simulation s WHERE s.simulation_id = tax_simulation_scenario.simulation_id));

ALTER TABLE tax_simulation_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE tax_simulation_memory FORCE ROW LEVEL SECURITY;
CREATE POLICY tax_simulation_memory_tenant_policy ON tax_simulation_memory
    USING (EXISTS (SELECT 1 FROM tax_simulation s WHERE s.simulation_id = tax_simulation_memory.simulation_id));

CREATE OR REPLACE FUNCTION reject_simulation_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'tax simulations are immutable';
END;
$$;

CREATE TRIGGER tax_simulation_immutable BEFORE UPDATE OR DELETE ON tax_simulation
FOR EACH ROW EXECUTE FUNCTION reject_simulation_mutation();

CREATE TRIGGER tax_simulation_scenario_immutable BEFORE UPDATE OR DELETE ON tax_simulation_scenario
FOR EACH ROW EXECUTE FUNCTION reject_simulation_mutation();

CREATE TRIGGER tax_simulation_memory_immutable BEFORE UPDATE OR DELETE ON tax_simulation_memory
FOR EACH ROW EXECUTE FUNCTION reject_simulation_mutation();

CREATE INDEX tax_simulation_tenant_created_idx ON tax_simulation(tenant_id, created_at DESC);

ALTER TABLE outbox_event ENABLE ROW LEVEL SECURITY;
ALTER TABLE outbox_event FORCE ROW LEVEL SECURITY;
CREATE POLICY outbox_event_tenant_policy ON outbox_event
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE INDEX outbox_simulation_unpublished_idx ON outbox_event(tenant_id, occurred_at)
    WHERE published_at IS NULL AND event_type LIKE 'tax.simulation.%';
