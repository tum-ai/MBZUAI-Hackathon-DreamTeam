import asyncio
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load env vars
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox-kesava", "langgraph", ".env"))
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

print(f"K2_LLM_URI present: {'K2_LLM_URI' in os.environ}")
print(f"K2_LLM_API_KEY present: {'K2_LLM_API_KEY' in os.environ}")

# Add repo root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("Importing app...")
from llm_new.agent import app
print("App imported.")


async def main():
    print("--- Starting Test ---")
    
    query = "Change the button color to red and then click it."
    print(f"Query: {query}")
    
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "session_id": "test-session",
        "next_action": {}
    }
    
    try:
        final_state = await app.ainvoke(initial_state)
        print("\n--- Final State Messages ---")
        for msg in final_state['messages']:
            print(f"[{type(msg).__name__}]: {msg.content[:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
