"""
Test runner for clarifier agent.
Executes all 15 tests in parallel for maximum efficiency.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

from llm.clarifier.tests.test_definitions import get_all_tests
from llm.clarifier.tests.validator import run_all_validations, generate_test_summary, generate_overall_summary


# Configuration
API_BASE_URL = "http://localhost:8000"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
TIMEOUT = 120  # seconds per request


def get_test_run_dir():
    """Get or create a timestamped directory for this test run."""
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(exist_ok=True)
    
    existing_runs = [d for d in RESULTS_DIR.iterdir() if d.is_dir() and d.name.startswith("run-")]
    if existing_runs:
        numbers = []
        for d in existing_runs:
            try:
                num = int(d.name.split("-")[1])
                numbers.append(num)
            except (IndexError, ValueError):
                pass
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1
    
    run_dir = RESULTS_DIR / f"run-{next_num}"
    run_dir.mkdir(exist_ok=True)
    return run_dir


def ensure_results_dir():
    """Ensure results directory exists."""
    RESULTS_DIR.mkdir(exist_ok=True)


async def send_clarify_request(client, session_id, step_id, intent, context):
    """Send single request to clarifier API."""
    url = f"{API_BASE_URL}/clarify"
    payload = {
        "session_id": session_id,
        "step_id": step_id,
        "intent": intent,
        "context": context
    }
    
    try:
        response = await client.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        return {"error": "Request timeout"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}


async def run_single_test(test, client):
    """Run a single test case."""
    test_start = time.time()
    
    print(f"[{test['id']}] Running: {test['name']}")
    
    # Send request
    response = await send_clarify_request(
        client,
        test["session_id"],
        test["step_id"],
        test["intent"],
        test["context"]
    )
    
    test_duration = time.time() - test_start
    
    # Prepare input data for summary
    input_data = {
        "session_id": test["session_id"],
        "step_id": test["step_id"],
        "intent": test["intent"],
        "context": test["context"]
    }
    
    # Validate response
    if "error" in response:
        result = generate_test_summary(
            test["id"],
            test["name"],
            test.get("description", ""),
            input_data,
            response,
            {"error": True},
            False,
            [response["error"]],
            {},
            test_duration
        )
    else:
        # Run validations
        assertions, passed, errors, quality_metrics = run_all_validations(test, response)
        
        result = generate_test_summary(
            test["id"],
            test["name"],
            test.get("description", ""),
            input_data,
            response,
            assertions,
            passed,
            errors,
            quality_metrics,
            test_duration
        )
    
    # Status indicator
    status = "✓" if result["passed"] else "✗"
    print(f"[{test['id']}] {status} Completed in {test_duration:.2f}s")
    
    return result


async def check_server_health():
    """Check if server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return True
    except Exception:
        pass
    return False


async def run_all_tests():
    """Run all clarifier tests in parallel."""
    print("=" * 60)
    print("CLARIFIER AGENT TEST SUITE")
    print("=" * 60)
    
    # Check server health
    print("\nChecking server health...")
    if not await check_server_health():
        print(f"❌ Error: Server not running at {API_BASE_URL}")
        print("\nStart the server with:")
        print("  cd /Users/georgychomakhashvili/MBZUAI-Hackathon-DreamTeam")
        print("  ./llm/venv/bin/python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000")
        return
    
    print("✓ Server is healthy")
    
    # Ensure results directory exists and get run directory
    ensure_results_dir()
    run_dir = get_test_run_dir()
    
    # Get all tests
    tests = get_all_tests()
    
    print(f"\nRunning {len(tests)} tests in parallel...")
    print(f"Results will be saved to: {run_dir.name}/")
    print()
    
    overall_start = time.time()
    
    # Run all tests in parallel with increased connection limits
    limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)
    async with httpx.AsyncClient(limits=limits, timeout=TIMEOUT) as client:
        test_tasks = [run_single_test(test, client) for test in tests]
        test_results = await asyncio.gather(*test_tasks)
    
    overall_duration = time.time() - overall_start
    
    # Generate overall summary
    overall_summary = generate_overall_summary(test_results, overall_duration)
    
    # Save overall summary
    summary_file = run_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(overall_summary, f, indent=2)
    
    # Print final results
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests:       {overall_summary['total_tests']}")
    print(f"Passed:            {overall_summary['passed']} ({overall_summary['success_rate']})")
    print(f"Failed:            {overall_summary['failed']}")
    print(f"Duration:          {overall_summary['total_duration_seconds']}s")
    print(f"\nResults saved to: {run_dir}")
    print("=" * 60)
    
    # Print quality metrics
    print("\nQUALITY METRICS (K2 Think Model Evaluation)")
    print("=" * 60)
    qm = overall_summary['quality_metrics']
    print(f"Replies reference context:  {qm['replies_reference_context']}")
    print(f"Replies ask questions:      {qm['replies_ask_questions']}")
    print(f"Jarvis personality present: {qm['jarvis_personality']}")
    print("=" * 60)
    
    # List any failed tests
    failed_tests = [t for t in test_results if not t.get("passed", False)]
    
    if failed_tests:
        print("\nFailed Tests:")
        for ft in failed_tests:
            print(f"  ✗ {ft['test_id']}: {ft['name']}")
            if ft.get('errors'):
                for error in ft['errors']:
                    print(f"    Error: {error}")
    else:
        print("\n🎉 All tests passed!")
    
    # Show quality metrics breakdown by category
    print("\n" + "=" * 60)
    print("QUALITY METRICS BY TEST")
    print("=" * 60)
    
    for test in test_results:
        qm = test.get("quality_metrics", {})
        status = "✓" if test.get("passed", False) else "✗"
        
        context_ref = "✓" if qm.get("reply_references_context", False) else "✗"
        asks_q = "✓" if qm.get("reply_asks_question", False) else "✗"
        jarvis = "✓" if qm.get("jarvis_personality_present", False) else "✗"
        
        print(f"{status} {test['test_id']}: Context:{context_ref} Question:{asks_q} Jarvis:{jarvis}")
    
    print("=" * 60)
    
    # Show sample replies
    print("\nSample Clarification Replies:")
    print("=" * 60)
    for i, test in enumerate(test_results[:3], 1):  # Show first 3
        if test.get("response") and "reply" in test["response"]:
            print(f"\n{i}. {test['test_id']} - {test['name']}")
            print(f"   Input: {test['input']['intent'][:60]}...")
            print(f"   Reply: {test['response']['reply'][:150]}...")
    
    print("\n" + "=" * 60)
    
    return overall_summary


def main():
    """Main entry point."""
    try:
        summary = asyncio.run(run_all_tests())
        
        # Exit with error code if any tests failed
        if summary and summary["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

