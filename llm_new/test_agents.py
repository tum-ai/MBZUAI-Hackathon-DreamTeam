"""
Test the refactored agent tools individually.
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Load environment variables
env_path = Path(__file__).resolve().parents[1] / "sandbox-kesava" / "langgraph" / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"Loading .env from: {env_path}")
else:
    print(f"Warning: .env not found at {env_path}")

# Import the new agents
from llm_new.clarifier_agent import generate_clarification_llm
from llm_new.editor_agent import generate_code_llm
from llm_new.actor_agent import generate_action_llm


async def test_clarifier():
    """Test the clarifier agent."""
    print("\n" + "="*60)
    print("Testing Clarifier Agent")
    print("="*60)
    
    intent = "User wants to make it bigger"
    context = "User just added a button to the page"
    
    try:
        result = await generate_clarification_llm(intent, context)
        print(f"✓ Clarifier Result: {result}")
        return True
    except Exception as e:
        print(f"✗ Clarifier Error: {str(e)}")
        return False


async def test_editor():
    """Test the editor agent."""
    print("\n" + "="*60)
    print("Testing Editor Agent")
    print("="*60)
    
    intent = "Create a submit button"
    context = "User wants to build a contact form"
    
    try:
        result = await generate_code_llm(intent, context)
        print(f"✓ Editor Result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"✗ Editor Error: {str(e)}")
        return False


async def test_actor():
    """Test the actor agent."""
    print("\n" + "="*60)
    print("Testing Actor Agent")
    print("="*60)
    
    intent = "User wants to scroll down"
    context = "User is viewing the homepage"
    
    try:
        result = await generate_action_llm(intent, context, "test_session", "test_step")
        print(f"✓ Actor Result: {result[:200]}...")
        return True
    except Exception as e:
        print(f"✗ Actor Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing Refactored Agents")
    print("="*60)
    
    # Check environment
    if not os.getenv("K2_API_KEY"):
        print("✗ Error: K2_API_KEY not found in environment")
        return
    
    print(f"✓ K2_API_KEY loaded")
    print(f"✓ K2_LLM_URI: {os.getenv('K2_LLM_URI', 'Using default')}")
    
    # Run tests
    results = {}
    
    results['clarifier'] = await test_clarifier()
    results['editor'] = await test_editor()
    results['actor'] = await test_actor()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
