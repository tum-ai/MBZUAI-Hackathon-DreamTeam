"""
Simple test for editor agent with verbose logging.
"""
import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables
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

from llm_new.editor_agent import generate_code_llm


async def main():
    print("\n" + "="*60)
    print("Testing Editor Agent with Verbose Logging")
    print("="*60)
    
    # Check environment
    api_key = os.getenv("K2_LLM_API_KEY")
    if not api_key:
        print("✗ Error: K2_LLM_API_KEY not found")
        return False
    
    print(f"✓ K2_LLM_API_KEY loaded: {api_key[:10]}...")
    
    # Test case: Create a button
    intent = "Add a new iPhone 17 Air card with price €2000"
    context = "Existing cards are iPhone 17 Pro and iPhone 17 Pro Max. Adding a third card."
    
    print(f"\nIntent: {intent}")
    print(f"Context: {context}")
    print("\nGenerating component...")
    print("="*60)
    
    try:
        result = await generate_code_llm(intent, context)
        print("\n" + "="*60)
        print("✓ Success!")
        print("="*60)
        print(f"Component JSON:\n{result}")
        
        # Try to parse it
        import json
        component = json.loads(result)
        print(f"\n✓ Valid JSON!")
        print(f"Component ID: {component.get('id')}")
        print(f"Component Type: {component.get('type')}")
        
        return True
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ Error: {str(e)}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
