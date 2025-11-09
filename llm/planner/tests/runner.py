"""
Test runner for planner agent.
Executes tests in parallel sessions while maintaining sequential order within each session.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import sys
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

from llm.planner.tests.test_definitions import TEST_SESSIONS, get_tests_by_session, get_session_ids
from llm.planner.tests.validator import run_all_validations, generate_session_summary, generate_overall_summary


# Configuration
API_BASE_URL = "http://localhost:8000"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
TIMEOUT = 120  # seconds per request


def get_test_run_dir():
    """Get or create a timestamped directory for this test run."""
    # Find next available session number
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(exist_ok=True)
    
    existing_sessions = [d for d in RESULTS_DIR.iterdir() if d.is_dir() and d.name.startswith("run-")]
    if existing_sessions:
        # Extract numbers and find max
        numbers = []
        for d in existing_sessions:
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


async def send_request(client, session_id, text, step_id):
    """Send single request to planner API."""
    url = f"{API_BASE_URL}/decide"
    payload = {
        "sid": session_id,
        "text": text,
        "step_id": step_id,
    }
    
    try:
        response = await client.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        result = response.json()
        
        # Handle list response (new format) - for single-task tests, return first item
        if isinstance(result, list):
            if len(result) > 0:
                return result[0]
            else:
                return {"error": "Empty response list"}
        
        return result
    except httpx.TimeoutException:
        return {"error": "Request timeout"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": str(e)}


async def run_session_tests(session_id, client, run_dir):
    """Run all tests for a single session sequentially."""
    print(f"\n[{session_id}] Starting session tests...")
    
    tests = get_tests_by_session(session_id)
    results = []
    all_step_ids = set()
    session_prompts = []
    
    session_start = time.time()
    
    for i, test in enumerate(tests, 1):
        test_start = time.time()
        
        print(f"[{session_id}] Running test {i}/{len(tests)}: {test['name']}")
        
        # Send request
        request_step_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{session_id}-{test['id']}-{i}"))

        response = await send_request(client, session_id, test["text"], request_step_id)
        
        test_duration = time.time() - test_start
        
        # Track prompts for session validation
        session_prompts.append(test["text"])
        
        # Validate response
        if "error" in response:
            result = {
                "test_id": test["id"],
                "name": test["name"],
                "description": test.get("description", ""),
                "input": {
                    "sid": session_id,
                    "text": test["text"],
                    "step_id": request_step_id,
                },
                "response": response,
                "assertions": {"error": True},
                "passed": False,
                "error": response["error"],
                "duration_seconds": round(test_duration, 2)
            }
        else:
            # Run validations
            assertions, passed, errors = run_all_validations(
                test, response, all_step_ids, session_prompts
            )
            
            result = {
                "test_id": test["id"],
                "name": test["name"],
                "description": test.get("description", ""),
                "expected_intent": test.get("expected_intent", "N/A"),
                "input": {
                    "sid": session_id,
                    "text": test["text"],
                    "step_id": request_step_id,
                },
                "response": response,
                "assertions": assertions,
                "passed": passed,
                "error": errors[0] if errors else None,
                "duration_seconds": round(test_duration, 2)
            }
        
        results.append(result)
        
        # Status indicator
        status = "✓" if result["passed"] else "✗"
        print(f"[{session_id}] Test {test['id']}: {status} ({test_duration:.2f}s)")
    
    session_duration = time.time() - session_start
    
    # Generate session summary
    summary = generate_session_summary(session_id, results, session_duration)
    
    # Save results in run directory
    session_file = run_dir / f"{session_id}.json"
    with open(session_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Save classification report
    classification_report = generate_classification_report(results, session_id)
    classification_file = run_dir / f"{session_id}_classification.json"
    with open(classification_file, "w") as f:
        json.dump(classification_report, f, indent=2)
    
    print(f"[{session_id}] Completed: {summary['passed']}/{summary['total_tests']} passed ({session_duration:.2f}s)")
    
    return summary


def generate_classification_report(results, session_id):
    """Generate detailed classification report."""
    correct = []
    incorrect = []
    
    for test in results:
        assertions = test.get("assertions", {})
        if "classification_correct" in assertions:
            classification_data = {
                "test_id": test["test_id"],
                "name": test["name"],
                "user_input": test["input"]["text"],
                "expected_intent": test.get("expected_intent", "N/A"),
                "actual_intent": assertions.get("intent_classification", "N/A"),
                "correct": assertions["classification_correct"]
            }
            
            if assertions["classification_correct"]:
                correct.append(classification_data)
            else:
                incorrect.append(classification_data)
    
    return {
        "session_id": session_id,
        "total_classified": len(correct) + len(incorrect),
        "correct": len(correct),
        "incorrect": len(incorrect),
        "accuracy": f"{(len(correct)/(len(correct)+len(incorrect))*100):.1f}%" if (len(correct)+len(incorrect)) > 0 else "N/A",
        "correct_classifications": correct,
        "incorrect_classifications": incorrect
    }


async def check_server_health():
    """Check if planner server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return True
    except Exception:
        pass
    return False


async def run_all_tests():
    """Run all test sessions in parallel."""
    print("=" * 60)
    print("PLANNER AGENT TEST SUITE")
    print("=" * 60)
    
    # Check server health
    print("\nChecking server health...")
    if not await check_server_health():
        print(f"❌ Error: Planner server not running at {API_BASE_URL}")
        print("\nStart the server with:")
        print("  source llm/venv/bin/activate")
        print("  python -m uvicorn llm.planner.server:app --host 0.0.0.0 --port 8000")
        return
    
    print("✓ Server is healthy")
    
    # Ensure results directory exists and get run directory
    ensure_results_dir()
    run_dir = get_test_run_dir()
    
    # Get session IDs
    session_ids = get_session_ids()
    total_tests = sum(len(TEST_SESSIONS[sid]["tests"]) for sid in session_ids)
    
    print(f"\nRunning {total_tests} tests across {len(session_ids)} sessions...")
    print("Sessions will run in parallel, tests within sessions run sequentially.")
    print(f"Results will be saved to: {run_dir.name}/")
    
    overall_start = time.time()
    
    # Run sessions in parallel
    async with httpx.AsyncClient() as client:
        session_tasks = [run_session_tests(session_id, client, run_dir) for session_id in session_ids]
        session_summaries = await asyncio.gather(*session_tasks)
    
    overall_duration = time.time() - overall_start
    
    # Generate overall summary
    overall_summary = generate_overall_summary(session_summaries, overall_duration)
    
    # Save overall summary in run directory
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
    print(f"Classification:    {overall_summary['classification_accuracy']} accurate")
    print(f"Duration:          {overall_summary['total_duration_seconds']}s")
    print(f"\nResults saved to: {run_dir}")
    print("=" * 60)
    
    # Print per-session breakdown
    print("\nPer-Session Results:")
    for session in session_summaries:
        status = "✓" if session["failed"] == 0 else "✗"
        print(f"  {status} {session['session_id']}: {session['passed']}/{session['total_tests']} passed")
    
    # List any failed tests
    failed_tests = []
    for session in session_summaries:
        for test in session["tests"]:
            if not test["passed"]:
                failed_tests.append({
                    "session": session["session_id"],
                    "test_id": test["test_id"],
                    "name": test["name"],
                    "error": test.get("error", "Unknown error")
                })
    
    if failed_tests:
        print("\nFailed Tests:")
        for ft in failed_tests:
            print(f"  ✗ [{ft['session']}] {ft['test_id']}: {ft['name']}")
            print(f"    Error: {ft['error']}")
    else:
        print("\n🎉 All tests passed!")
    
    # Show classification mismatches
    print("\n" + "=" * 60)
    print("CLASSIFICATION DETAILS")
    print("=" * 60)
    
    all_misclassifications = []
    for session in session_summaries:
        for test in session["tests"]:
            assertions = test.get("assertions", {})
            if "classification_correct" in assertions and not assertions["classification_correct"]:
                all_misclassifications.append({
                    "session": session["session_id"],
                    "test_id": test["test_id"],
                    "name": test["name"],
                    "input": test["input"]["text"],
                    "expected": test.get("expected_intent", "N/A"),
                    "actual": assertions.get("intent_classification", "N/A")
                })
    
    if all_misclassifications:
        print(f"\n⚠️  Classification Mismatches: {len(all_misclassifications)}")
        print("\nNote: Tests still PASS if system checks are OK. Misclassification may be valid LLM reasoning.\n")
        for mc in all_misclassifications:
            print(f"  [{mc['session']}] {mc['test_id']}: {mc['name']}")
            print(f"    Input:    \"{mc['input'][:60]}{'...' if len(mc['input']) > 60 else ''}\"")
            print(f"    Expected: {mc['expected']}")
            print(f"    Actual:   {mc['actual']}")
            print()
    else:
        print("\n✓ All classifications match expected intents!")
    
    print("=" * 60)
    
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

