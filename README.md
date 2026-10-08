# 🧊 Thermo-Query: Enterprise Cold-Chain Incident Control Agent

An **Agentic Supply Chain Telemetry & Compliance Orchestrator** built for real-time fleet risk monitoring, corridor weather assessment, and cold-chain Standard Operating Procedure (SOP) enforcement. Powered by **LangGraph**, **LangChain**, **PostgreSQL**, and **Pinecone Vector Search**.

---

## 🛠️ System Architecture

```text
                               +-----------------------------+
                               |     Dispatcher / CLI        |
                               |    (src/console_app.py)     |
                               +--------------+--------------+
                                              |
                                              v
                               +-----------------------------+
                               |   LangGraph Orchestrator    |
                               |   (src/orchestrator.py)     |
                               +--------------+--------------+
                                              |
                +-----------------------------+-----------------------------+
                |                             |                             |
                v                             v                             v
  +--------------------------+  +--------------------------+  +--------------------------+
  |    query_telemetry_db    |  | fetch_corridor_conditions|  |   search_compliance_sop  |
  |  (PostgreSQL View Tool)  |  |  (Live Telemetry & GPS)  |  |  (Pinecone Vector Search)|
  +-------------+------------+  +--------------------------+  +--------------------------+
                |                             |                             |
                v                             v                             v
                +-----------------------------+-----------------------------+
                                +--------------------------+
                                |  fde_views.agent_audit_log|
                                |   (Immutable SQL Logs)    |
                                +--------------------------+

```

---

## 📂 Project Structure

```text
thermo-query/
├── data/
│   ├── cache/
│   │   └── ingestion_hash_cache.json       # Ingestion deduplication hash cache
│   ├── policy/
│   │   └── Cold_Chain_Incident_SOP_v2.md     # Policy & SOP document for RAG vectorization
│   └── raw/
│       └── dynamic_supply_chain_logistics_dataset.csv  # Telemetry seed dataset
├── prompts/
│   └── system_prompt.txt                    # System prompt instructions
├── scripts/
│   ├── ingest_legacy_data.py               # Database ingestion script
│   ├── ingest_sop_pinecone.py              # Pinecone vector database indexer
│   ├── setup_audit_log.sql                 # Audit table schema & least-privilege grants
│   └── setup_security_and_view.sql         # Security views and user roles initialization
├── src/
│   ├── agent_tools.py                      # Telemetry DB, Open-Meteo, & Pinecone tool bindings
│   ├── console_app.py                      # Interactive CLI Dispatch Console & Audit Viewer
│   └── orchestrator.py                     # LangGraph state machine & LLM factory
├── .env                                    # Environment configuration
├── .gitignore
├── .python-version
├── docker-compose.yaml                     # PostgreSQL container configuration
├── pyproject.toml                          # Project configuration & dependencies
├── README.md                               # Project documentation
├── requirements.txt                        # Pip dependency manifest
└── uv.lock                                 # Lockfile for reproducible builds

```

---

## 🌟 Key Features

* **Multi-LLM Reasoning Engine:** Supports cloud reasoners (**Groq**, **OpenAI GPT-4o**) with local fallback to **Ollama (Qwen 2.5)**.
* **Least-Privilege Security Model:** Read-only access to PostgreSQL telemetry views (`fde_views.vw_active_fleet`) paired with strict append-only permissions for audit logs (`fde_views.agent_audit_log`).
* **SOP Vector RAG (Pinecone):** Fast semantic retrieval over regulatory guidelines and cold-chain emergency breach procedures.
* **Corridor Telemetry Tooling:** Live weather and route risk retrieval via Open-Meteo API integrations based on GPS coordinates.
* **Immutable Audit Trail:** Real-time interception and recording of tool invocations, inputs, raw outputs, and synthesized resolutions to database tables.
* **Interactive Dispatch CLI Console:** Multi-tab console supporting session management, real-time reasoning traces, and administrator audit log inspection.

---

## 🚀 Quickstart Guide

### 1. Prerequisites

* Python 3.10+
* Docker & Docker Compose
* Pinecone API Key
* Groq / OpenAI API Key (Optional for cloud reasoning models)

---

### 2. Environment Setup

Clone the repository and populate your `.env` file in the root directory:

```ini
# Database
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=legacy_db

# Vector DB
PINECONE_API_KEY=

# Embeddings
Embeddings_model=LOCAL        # LOCAL or OPENAI
Local_Embedding_Model=BAAI/bge-m3

# Models
GROQ_MODEL=openai/gpt-oss-120b
GROQ_API_KEY=

# Agent
SQL_AGENT_USER=usr_fde_ro
SQL_AGENT_PASSWORD=AgentPassword

# OpenAI
OPENAI_API_KEY=

```

---

### 3. Initialize Database & Services

Start the PostgreSQL service using Docker Compose:

```bash
docker compose up -d

```

Initialize database security roles, audit logs, and load seed data:

```bash
# 1. Setup Database Security & Views
docker exec -i legacy_postgres psql -U postgres -d legacy_db < scripts/setup_security_and_view.sql

# 2. Setup Audit Logging Table
docker exec -i legacy_postgres psql -U postgres -d legacy_db < scripts/setup_audit_log.sql

# 3. Ingest Fleet Telemetry Dataset
python scripts/ingest_legacy_data.py

# 4. Ingest SOP Documents into Pinecone Vector Index
python scripts/ingest_sop_pinecone.py

```

---

## 💻 Running the Application

Launch the Dispatch Console Center:

```bash
python src/console_app.py

```

### Console Options

1. **🧊 Dispatch Console:** Query fleet telemetry, check corridor conditions, and execute cold-chain incident resolutions.
2. **🛡️ Security & Audit Logs:** Authenticate as administrator to inspect real-time tool execution logs.
3. **🗑️ Reset Dispatch Workspace Session:** Generate a new session token and clear working state.

---

## 📊 Sample Agent Output

Example response generated by the orchestrator during a cold-chain incident evaluation:  
**Q:** What are the temperature rules for fresh perishables?  
**A:**  
  
**Temperature Rules for Fresh Perishables (Cold-Chain SOP)**

| Parameter | Required Range | Action if Exceeded |
| --- | --- | --- |
| **IoT-reported temperature** (`IOT_TEMP_VAL_C`) | **0.0 °C – 4.0 °C** | • Immediate cold-chain breach declared.<br>

<br>• Dispatcher contacts driver right away to restart the auxiliary cooling unit.<br>

<br>• If the estimated time-of-arrival (ETA) delay is **> 1 hour**, the vehicle must be diverted to the nearest emergency cold-storage facility. |

**Key Points**

* The temperature window (0 °C – 4 °C) is mandatory for all fresh-perishable cargo.
* Any reading above **4.0 °C** triggers the breach protocol above.
* The rule applies regardless of other risk factors; however, if the shipment is also classified as **High Risk** and the delay probability exceeds **0.65**, the issue must be escalated to the Tier 2 Logistics Manager in addition to the temperature-breach steps.