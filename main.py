import asyncio
import sys
import os
from dotenv import load_dotenv

# --- Imports for Memory ---
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graph.builder import get_graph_builder

# --- Setup Paths & Env ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(r"C:\Users\KIIT\Desktop\Projects\LangGraph\.env")

# --- Interactive Loop ---
async def main():
    print("---------------------------------------------------------")
    print("Multi-Agent System Initialized (Persistent Memory)")
    print("   - Type a Topic (e.g., 'London', 'Tesla').")
    print("   - Type 'exit' to quit.")
    print("---------------------------------------------------------")

    # 1. Ensure DB folder exists
    if not os.path.exists("database"):
        os.makedirs("database")

    # 2. OPEN THE DATABASE CONNECTION SAFELY
    # FIX: Use a normal file path, NOT "sqlite:///..."
    db_path = "database/checkpoints.db"
    
    async with AsyncSqliteSaver.from_conn_string(db_path) as memory:
        
        # 3. Compile the Graph HERE with the open memory
        builder = get_graph_builder()
        graph_app = builder.compile(checkpointer=memory)

        # 4. Session Config (Thread ID 1)
        config = {"configurable": {"thread_id": "1"}}

        while True:
            try:
                user_topic = input("\nEnter Topic: ").strip()
            except KeyboardInterrupt:
                break

            if user_topic.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
            
            if not user_topic: continue

            print("\n   Processing...")
            
            # Run the Graph
            initial_state = {"topic": user_topic, "results": []}
            final_state = await graph_app.ainvoke(initial_state, config=config)

            print(final_state["final_report"])

if __name__ == "__main__":
    try:
        # Fix for Windows Async Loop Policy
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass