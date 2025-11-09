"""
Test runner for orchestration pipeline.
Executes tests against /plan endpoint and generates comprehensive reports.
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with:")
    print("  cd llm && source venv/bin/activate && pip install httpx")
    sys.exit(1)

from llm.tests.test_definitions import get_all_tests
from llm.tests.validator import run_all_validations, generate_test_summary, generate_overall_summary


# Configuration
API_BASE_URL = "http://localhost:8000"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
TIMEOUT = 180  # seconds per request (longer for orchestration)


def get_test_run_dir():
    """Get or create a numbered directory for this test run."""
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


async def send_plan_request(client, sid, text):
    """Send request to /plan endpoint."""
    url = f"{API_BASE_URL}/plan"
    payload = {
        "sid": sid,
        "text": text
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
    
    # Send request to /plan endpoint
    response = await send_plan_request(
        client,
        test["sid"],
        test["text"]
    )
    
    test_duration = time.time() - test_start
    
    # Prepare input data for summary
    input_data = {
        "sid": test["sid"],
        "text": test["text"],
        "expected_tasks": test.get("expected_tasks", 1),
        "expected_agents": test.get("expected_agents", [])
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
        # Run validations with duration for per-task timing
        assertions, passed, errors, metrics = run_all_validations(test, response, test_duration)
        
        result = generate_test_summary(
            test["id"],
            test["name"],
            test.get("description", ""),
            input_data,
            response,
            assertions,
            passed,
            errors,
            metrics,
            test_duration
        )
    
    # Status indicator
    status = "✓" if result["passed"] else "✗"
    tasks_info = f"({result.get('metrics', {}).get('actual_tasks', 0)} tasks)"
    print(f"[{test['id']}] {status} Completed in {test_duration:.2f}s {tasks_info}")
    
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
    """Run all orchestration tests."""
    print("=" * 70)
    print("ORCHESTRATION PIPELINE TEST SUITE")
    print("=" * 70)
    
    # Check server health
    print("\nChecking server health...")
    if not await check_server_health():
        print(f"❌ Error: Server not running at {API_BASE_URL}")
        print("\nStart the server with:")
        print("  cd llm && source venv/bin/activate")
        print("  python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000")
        return
    
    print("✓ Server is healthy")
    
    # Ensure results directory exists and get run directory
    ensure_results_dir()
    run_dir = get_test_run_dir()
    
    # Get all tests
    tests = get_all_tests()
    
    print(f"\nRunning {len(tests)} tests sequentially...")
    print(f"Results will be saved to: {run_dir.name}/")
    print()
    
    overall_start = time.time()
    
    # Run all tests sequentially to measure actual timing
    test_results = []
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for i, test in enumerate(tests, 1):
            print(f"\n--- Test {i}/{len(tests)} ---")
            result = await run_single_test(test, client)
            test_results.append(result)
    
    overall_duration = time.time() - overall_start
    
    # Generate overall summary
    overall_summary = generate_overall_summary(test_results, overall_duration)
    
    # Save overall summary
    summary_file = run_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(overall_summary, f, indent=2)
    
    # Print final results
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total Tests:          {overall_summary['total_tests']}")
    print(f"Passed:               {overall_summary['passed']} ({overall_summary['success_rate']})")
    print(f"Failed:               {overall_summary['failed']}")
    print(f"Total Duration:       {overall_summary['total_duration_seconds']}s")
    print(f"Average Test Time:    {overall_summary['average_test_duration']}s")
    print(f"Average Per Task:     {overall_summary['average_per_task']}s")
    print(f"Average Planner Time: {overall_summary.get('average_planner_time', 0)}s")
    print(f"Total Tasks Executed: {overall_summary['total_tasks_executed']}")
    print(f"Routing Accuracy:     {overall_summary['routing_accuracy']}")
    print(f"\nResults saved to: {run_dir}")
    print("=" * 70)
    
    # List any failed tests
    failed_tests = [t for t in test_results if not t.get("passed", False)]
    
    if failed_tests:
        print("\n❌ Failed Tests:")
        for ft in failed_tests:
            print(f"  ✗ {ft['test_id']}: {ft['name']}")
            if ft.get('errors'):
                for error in ft['errors'][:3]:  # Show first 3 errors
                    print(f"    - {error}")
    else:
        print("\n🎉 All tests passed!")
    
    # Show agent distribution
    print("\n" + "=" * 70)
    print("AGENT DISTRIBUTION")
    print("=" * 70)
    agent_dist = overall_summary['agent_distribution']
    for agent, count in sorted(agent_dist.items()):
        print(f"  {agent.upper()}: {count} tasks")
    
    # Show average per agent type
    print("\n" + "=" * 70)
    print("AVERAGE TIME PER AGENT TYPE")
    print("=" * 70)
    agent_averages = overall_summary.get('average_per_agent_type', {})
    for agent, avg_time in sorted(agent_averages.items()):
        print(f"  {agent.upper():10s} {avg_time:.3f}s per task")
    
    # Show timing breakdown with task details
    print("\n" + "=" * 70)
    print("TIMING BREAKDOWN (Top 5 Slowest Tests)")
    print("=" * 70)
    timing_sorted = sorted(
        overall_summary['timing_breakdown'],
        key=lambda x: x['duration_seconds'],
        reverse=True
    )
    for item in timing_sorted[:5]:
        print(f"\n  {item['test_id']}: {item['name']}")
        print(f"  Description: {item['description']}")
        print(f"  Total: {item['duration_seconds']:.2f}s | Tasks: {item['task_count']} | Avg/Task: {item['average_per_task']:.2f}s")
        
        # Show planner and overhead if available
        if item.get('planner_time_seconds', 0) > 0:
            print(f"  Breakdown: Planner {item['planner_time_seconds']:.2f}s | Agents {item.get('total_agent_time_seconds', 0):.2f}s | Overhead {item.get('orchestrator_overhead_seconds', 0):.2f}s")
        
        if item.get('tasks'):
            for task in item['tasks']:
                duration = task.get('duration_seconds', 0)
                print(f"    └─ Task {task['task_number']}: [{task['agent_type'].upper()}] {task['intent'][:50]}... ({duration:.2f}s)")
    
    # Show sample outputs by agent type
    print("\n" + "=" * 70)
    print("SAMPLE OUTPUTS BY AGENT TYPE")
    print("=" * 70)
    
    # Find one example of each agent type
    agent_samples = {"edit": None, "act": None, "clarify": None}
    for test in test_results:
        if not test.get("passed"):
            continue
        response = test.get("response", {})
        results = response.get("results", [])
        for result in results:
            agent_type = result.get("agent_type")
            if agent_type in agent_samples and agent_samples[agent_type] is None:
                agent_samples[agent_type] = {
                    "test_id": test["test_id"],
                    "intent": result.get("intent", "")[:60],
                    "output": result.get("result", "")[:150]
                }
    
    for agent_type, sample in agent_samples.items():
        if sample:
            print(f"\n{agent_type.upper()} Agent Sample:")
            print(f"  Test: {sample['test_id']}")
            print(f"  Intent: {sample['intent']}...")
            print(f"  Output: {sample['output']}...")
    
    print("\n" + "=" * 70)
    
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

