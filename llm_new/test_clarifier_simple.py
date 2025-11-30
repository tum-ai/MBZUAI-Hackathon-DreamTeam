"""
Simple test for clarifier agent only.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables from multiple possible locations
env_paths = [
    Path(__file__).resolve().parents[1] / "sandbox-kesava" / "langgraph" / ".env",
    Path(__file__).resolve().parents[1] / ".env",
    Path.cwd() / ".env",
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loading .env from: {env_path}")
        break
else:
    print("Warning: No .env file found")

from llm_new.clarifier_agent import generate_clarification_llm


async def main():
    print("\n" + "="*60)
    print("Testing Clarifier Agent")
    print("="*60)
    
    # Check environment
    api_key = os.getenv("K2_LLM_API_KEY")
    if not api_key:
        print("✗ Error: K2_LLM_API_KEY not found")
        return False
    
    print(f"✓ K2_LLM_API_KEY loaded: {api_key[:10]}...")
    
    intent = "User wants to make it bigger"
    context = "User just added a button to the page"
    
    print(f"Intent: {intent}")
    print(f"Context: {context}")
    print("\nGenerating clarification...")
    
    try:
        result = await generate_clarification_llm(intent, context)
        print(f"\n✓ Success!")
        print(f"Clarification: {result}")
        return True
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
