import os
import sys
import uuid
import json
import urllib.parse
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_core.messages import HumanMessage, ToolMessage


# IMMEDIATE PATH & ENVIRONMENT RESOLUTION
# --------------------------------------------

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

load_dotenv(project_root / ".env", override=True)

# Import the compiled graph
from src.orchestrator import agent


# POSTGRESQL CREDENTIALS & AUDIT LOGGING
# ---------------------------------------------

db_host = os.getenv("POSTGRES_HOST", os.getenv("SQL_SERVER_HOST", "localhost"))
db_port = os.getenv("POSTGRES_PORT", "5432")
db_name = os.getenv("POSTGRES_DB", "legacy_db")
db_user = os.getenv("SQL_AGENT_USER", "usr_fde_ro")
db_password = os.getenv("SQL_AGENT_PASSWORD", "AgentPassword")

# Engine for the Agent to write audit logs using restricted agent permissions
escaped_password = urllib.parse.quote_plus(db_password) if db_password else ""
db_url = f"postgresql+psycopg2://{db_user}:{escaped_password}@{db_host}:{db_port}/{db_name}"
log_engine = create_engine(db_url)

def write_audit_log(session_id: str, node_name: str, tool_name: str, content: str):
    """writes agent execution traces to fde_views.agent_audit_log."""
    try:
        with log_engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO fde_views.agent_audit_log (session_id, node_executed, tool_name, content)
                VALUES (:session_id, :node_name, :tool_name, :content)
            """), {
                "session_id": session_id,
                "node_name": node_name,
                "tool_name": tool_name,
                "content": content
            })
            conn.commit()
    except Exception as e:
        print(f"⚠️ Audit Log Failed (Silent): {e}")


# DISPATCH CONSOLE EXECUTION LOOP
# -----------------------------------------------------
def run_dispatch_console(session_id: str):
    thread_config = {"configurable": {"thread_id": session_id}}
    print("\n" + "-"*60)
    print("🧊 FDE Cold-Chain Incident Control Console")
    print(f"Active Session Token: [{session_id[:8]}...]")
    print("Type 'back' to return to menu, or 'exit' to quit.")
    print("-"*60 + "\n")

    while True:
        try:
            user_input = input("\nDispatcher > ")
            if user_input.strip().lower() in ['exit', 'quit']:
                sys.exit(0)
            if user_input.strip().lower() == 'back':
                break
            if not user_input.strip():
                continue

            final_response = ""
            
            print("\n🧠 Initializing Core Reasoner Node...")
            events = agent.stream(
                {"messages": [HumanMessage(content=user_input)]}, 
                config=thread_config,
                stream_mode="updates"
            )

            for event in events:
                for node_name, node_state in event.items():
                    
                    if node_name == "reasoner":
                        latest_msg = node_state["messages"][-1]
                        
                        # A. Intercept Tool Call Requests (Inputs)
                        if hasattr(latest_msg, "tool_calls") and latest_msg.tool_calls:
                            for tool_call in latest_msg.tool_calls:
                                print(f"⚡ [Intent]: `{tool_call['name']}`")
                                print(f"📥 [Generated Input]: {json.dumps(tool_call['args'], indent=2)}")
                                
                                write_audit_log(
                                    session_id=session_id,
                                    node_name="reasoner",
                                    tool_name=tool_call['name'],
                                    content=json.dumps(tool_call['args'])
                                )
                        
                        # B. Intercept Final Generation
                        if latest_msg.content:
                            final_response = latest_msg.content
                            write_audit_log(
                                session_id=session_id,
                                node_name="reasoner_final",
                                tool_name="LLM Text Synthesis",
                                content=final_response
                            )
                            
                    elif node_name == "tools":
                        print("🔧 Executing Subsystem Tools...")
                        for msg in node_state.get("messages", []):
                            if isinstance(msg, ToolMessage):
                                print(f"📤 [Tool Output ({msg.name})]:\n{msg.content}\n")
                                write_audit_log(
                                    session_id=session_id,
                                    node_name="tools",
                                    tool_name=msg.name,
                                    content=msg.content
                                )

            if final_response:
                print(f"\n🤖 FDE Agent Resolution:\n{final_response}\n")
            else:
                print("\n⚠️ Execution Timeout: System encountered an unresolved processing edge case.")

        except (KeyboardInterrupt, EOFError):
            print("\nReturning to main menu...")
            break


# AUDIT LOG VIEWER (ADMIN AUTHENTICATED)
# ----------------------------------------------

def view_audit_logs():
    print("\n" + "-"*60)
    print("🛡️ Enterprise Agent Audit Trail Viewer")
    print("-"*60)
    
    admin_user = input("Admin Username (or press Enter for superuser 'postgres'): ").strip() or "postgres"
    admin_pass = input("Admin Password: ").strip()

    try:
        escaped_admin_pass = urllib.parse.quote_plus(admin_pass) if admin_pass else ""
        admin_db_url = f"postgresql+psycopg2://{admin_user}:{escaped_admin_pass}@{db_host}:{db_port}/{db_name}"
        admin_engine = create_engine(admin_db_url)

        with admin_engine.connect() as conn:
            query = """
                SELECT log_id, timestamp, session_id, node_executed, tool_name, content 
                FROM fde_views.agent_audit_log 
                ORDER BY timestamp DESC
                LIMIT 20;
            """
            df = pd.read_sql(text(query), conn)

        print("\n✅ Authorization Successful. Showing latest 20 audit entries:\n")
        if not df.empty:
            print(df.to_string(index=False))
        else:
            print("No audit logs found in the database.")
            
    except Exception as e:
        print(f"\n❌ Database Query Failed: {e}")

    input("\nPress Enter to return to main menu...")


# CLI MENU ROUTER
# --------------------------------------

def main():
    session_id = str(uuid.uuid4())

    while True:
        print("\n" + "-"*45)
        print("          COMMAND CENTER (CLI)          ")
        print("-"*45)
        print(f"Current Session: [{session_id[:8]}...]")
        print("1. 🧊 Dispatch Console (Chat CLI)")
        print("2. 🛡️ Security & Audit Logs")
        print("3. 🗑️ Reset Dispatch Workspace Session")
        print("4. ❌ Exit")
        print("-"*45)

        choice = input("Select Option (1-4): ").strip()

        if choice == "1":
            run_dispatch_console(session_id)
        elif choice == "2":
            view_audit_logs()
        elif choice == "3":
            session_id = str(uuid.uuid4())
            print(f"\n✅ Session deleted. New Session ID: [{session_id[:8]}...]")
        elif choice == "4":
            print("\nExiting Command Center.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()