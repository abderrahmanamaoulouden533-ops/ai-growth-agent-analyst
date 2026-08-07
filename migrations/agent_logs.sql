-- migrations/agent_logs.sql
-- Schéma de la table centralisée des logs (Phase A) + tables Phase B

CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    agent_name TEXT NOT NULL,
    action_type TEXT NOT NULL,
    input_summary TEXT,
    output_summary TEXT,
    lead_id TEXT,
    client_id TEXT NOT NULL,
    model_used TEXT,
    latency_ms INTEGER,
    timestamp TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_lookup ON agent_logs (client_id, agent_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_lead ON agent_logs (lead_id, timestamp DESC);

-- Tables Phase B
CREATE TABLE IF NOT EXISTS leads (
    lead_id UUID PRIMARY KEY,
    client_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    source TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    industry_segment TEXT,
    qualification_score INTEGER,
    lead_stage TEXT DEFAULT 'new',
    last_action TEXT,
    last_action_at TIMESTAMPTZ,
    messages_sent INTEGER DEFAULT 0,
    meeting_date TIMESTAMPTZ,
    notes JSONB DEFAULT '[]'::jsonb,
    contract_value DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS ad_spend (
    id SERIAL PRIMARY KEY,
    client_id TEXT NOT NULL,
    campaign_id TEXT,
    platform TEXT,
    spend DECIMAL(10,2),
    date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    lead_id UUID,
    booked_at TIMESTAMPTZ,
    showed_up BOOLEAN DEFAULT NULL,
    FOREIGN KEY (lead_id) REFERENCES leads(lead_id)
);
CREATE TABLE IF NOT EXISTS landing_page_stats (
    id SERIAL PRIMARY KEY,
    client_id TEXT NOT NULL,
    page_url TEXT NOT NULL,
    visitors INTEGER DEFAULT 0,
    form_submissions INTEGER DEFAULT 0,
    date DATE NOT NULL,
    UNIQUE(client_id, page_url, date)
);