import asyncio
import sys
import os
from pathlib import Path  
from dotenv import load_dotenv

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from graph.builder import get_graph_builder


BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

load_dotenv(env_path)


async def main():
    print("---------------------------------------------------------")
    print("Pregelflow - News, Weather, and Stock Update Agent")
    print("this entire architecture was build using LangGraph(mostly pregel, persistence with sqlite, async calls, etc.)")
    print("   - Type somthing to get news, weather, and stock updates")
    print("   - Type 'exit' to quit.")
 

 
    if not os.path.exists("database"):
        os.makedirs("database")
    db_path = "database/checkpoints.db"
    
    async with AsyncSqliteSaver.from_conn_string(db_path) as memory:
        
        #Compile the graph with memory
        builder = get_graph_builder()
        graph_app = builder.compile(checkpointer=memory)

        #Session config 
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

            print("\nProcessing...")
            
            # Run the Graph
            initial_state = {"topic": user_topic, "results": []}
            final_state = await graph_app.ainvoke(initial_state, config=config)

            print(final_state["final_report"])

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass