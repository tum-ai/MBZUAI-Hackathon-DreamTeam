import os
import sys
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Add repo root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load env vars
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox-kesava", "langgraph", ".env"))
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Import app after env vars are loaded
from llm_new.server import app

client = TestClient(app)

def test_plan_endpoint():
    print("\n--- Testing /plan endpoint ---")
    payload = {
        "sid": "test-session-api",
        "text": "Change the button color to blue",
        "step_id": "step-1"
    }
    
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = client.post("/plan", json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error Response:")
            print(response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_plan_endpoint()
