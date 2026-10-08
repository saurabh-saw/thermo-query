-- AGENT AUDIT LOGGING TABLE (PostgreSQL)
-- Purpose: Log LLM node executions, tool calls, and outputs safely

-- Create the Audit Log Table in fde_views schema
CREATE TABLE IF NOT EXISTS fde_views.agent_audit_log (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(50),
    node_executed VARCHAR(50),
    tool_name VARCHAR(100),
    content TEXT
);

-- Grant the read-only agent user permission to INSERT into the audit table
GRANT INSERT ON fde_views.agent_audit_log TO usr_fde_ro;

-- Grant sequence permissions so usr_fde_ro can generate auto-incrementing log_ids
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA fde_views TO usr_fde_ro;