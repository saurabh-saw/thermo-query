-- SECURITY & SEMANTIC LAYER SCRIPT (PostgreSQL)
-- Purpose: Protect tables from LLM mutations & restrict access
-- --------------------------------------------------------------------

-- Create a dedicated schema for clean AI views
CREATE SCHEMA IF NOT EXISTS fde_views;

-- Create the Semantic View (Translating legacy junk to clean aliases)
CREATE OR REPLACE VIEW fde_views.vw_active_fleet AS
SELECT 
    "TS_UTC" AS "Timestamp",
    "V_LAT" AS "Latitude",
    "V_LON" AS "Longitude",
    "IOT_TEMP_VAL_C"::FLOAT AS "Current_Temperature_C",
    "CGO_COND_CD" AS "Cargo_Condition_Code",
    "RISK_CLS_TXT" AS "Risk_Classification",
    "DELAY_PROB_DEC" AS "Delay_Probability",
    "PRT_CNG_LVL" AS "Port_Congestion_Level",
    "RT_RSK_IDX" AS "Route_Risk_Index"
FROM public.tbl_sc_fleet_hist_raw;

-- Create a strict Read-Only User for the AI Agent
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'usr_fde_ro') THEN
        CREATE USER usr_fde_ro WITH PASSWORD 'AgentPassword';
    END IF;
END
$$;

-- Grant access ONLY to the semantic view schema
GRANT CONNECT ON DATABASE legacy_db TO usr_fde_ro;
GRANT USAGE ON SCHEMA fde_views TO usr_fde_ro;
GRANT SELECT ON fde_views.vw_active_fleet TO usr_fde_ro;

-- Explicitly isolate the public/raw data schema from the agent
REVOKE ALL ON SCHEMA public FROM usr_fde_ro;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM usr_fde_ro;