"""
Multi-task test runner for planner agent queue system.
Tests task splitting, queue management, and context propagation.
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)

from llm.planner.tests.multitask_test_definitions import (
    get_all_multitask_tests,
    get_multitask_tests_by_session,
    get_multitask_session_ids
)

# Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 120.0
RESULTS_DIR = Path(__file__).parent / "results"


def get_next_run_dir():
    """Get next available run directory."""
    RESULTS_DIR.mkdir(exist_ok=True)
    
    existing_runs = [d for d in RESULTS_DIR.iterdir() if d.is_dir() and d.name.startswith("multitask-run-")]
    
    if existing_runs:
        numbers = []
        for d in existing_runs:
            try:
                num = int(d.name.split("-")[-1])
                numbers.append(num)
            except (IndexError, ValueError):
                pass
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1
    
    run_dir = RESULTS_DIR / f"multitask-run-{next_num}"
    run_dir.mkdir(exist_ok=True)
    return run_dir


async def check_server_health():
    """Check if server is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False


async def send_multitask_request(client, session_id, text):
    """Send request and return full list response."""
    url = f"{API_BASE_URL}/decide"
    payload = {"sid": session_id, "text": text}
    
    try:
        response = await client.post(url, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        result = response.json()
        
        # Return the full list (don't extract first item like single-task tests)
        if isinstance(result, list):
            return {"success": True, "tasks": result, "count": len(result)}
        else:
            # Old format or error
            return {"success": False, "error": "Expected list response", "result": result}
    except httpx.TimeoutException:
        return {"success": False, "error": "Request timeout"}
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_queue_status(client, session_id):
    """Get queue status for session."""
    url = f"{API_BASE_URL}/queue/{session_id}"
    
    try:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return {"success": True, "status": response.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_multitask_response(response, test, all_step_ids):
    """Validate multi-task response."""
    assertions = {}
    errors = []
    passed = False
    
    # Check if request was successful
    if not response.get("success"):
        errors.append(f"Request failed: {response.get('error')}")
        return assertions, False, errors
    
    tasks = response.get("tasks", [])
    expected_count = test.get("expected_task_count", 1)
    
    # Validate task count
    actual_count = len(tasks)
    assertions["correct_task_count"] = actual_count == expected_count
    if actual_count != expected_count:
        errors.append(f"Expected {expected_count} tasks, got {actual_count}")
    
    # Validate each task
    expected_tasks = test.get("expected_tasks", [])
    for i, (task, expected) in enumerate(zip(tasks, expected_tasks)):
        task_prefix = f"task_{i+1}"
        
        # Check structure
        assertions[f"{task_prefix}_has_step_id"] = "step_id" in task
        assertions[f"{task_prefix}_has_step_type"] = "step_type" in task
        assertions[f"{task_prefix}_has_intent"] = "intent" in task
        assertions[f"{task_prefix}_has_context"] = "context" in task
        
        if "step_id" not in task:
            errors.append(f"Task {i+1}: Missing step_id")
            continue
        
        # Check step_id uniqueness
        step_id = task.get("step_id", "")
        if step_id in all_step_ids:
            assertions[f"{task_prefix}_unique_step_id"] = False
            errors.append(f"Task {i+1}: Duplicate step_id: {step_id}")
        else:
            assertions[f"{task_prefix}_unique_step_id"] = True
            all_step_ids.add(step_id)
        
        # Check step_type
        actual_type = task.get("step_type", "")
        expected_type = expected.get("step_type", "")
        acceptable_types = expected.get("acceptable_types", [expected_type])
        assertions[f"{task_prefix}_correct_type"] = actual_type in acceptable_types
        if actual_type not in acceptable_types:
            errors.append(f"Task {i+1}: Expected type '{expected_type}', got '{actual_type}'")
        
        # Check content contains expected text
        intent = task.get("intent", "").lower()
        contains_text = expected.get("contains", "").lower()
        assertions[f"{task_prefix}_contains_text"] = contains_text in intent
        if contains_text not in intent:
            errors.append(f"Task {i+1}: Intent doesn't contain '{contains_text}'")
    
    # Validate context propagation
    if test.get("validate_context_propagation") and len(tasks) > 1:
        for i in range(1, len(tasks)):
            context = tasks[i].get("context", "")
            # Second task should have context from first task
            if i == 1:
                assertions["task_2_has_context_from_task_1"] = len(context) > 0
                if len(context) == 0:
                    errors.append("Task 2 should have context from Task 1")
    
    # Check if single task should have context from previous requests
    if test.get("should_have_context") and len(tasks) == 1:
        context = tasks[0].get("context", "")
        assertions["has_previous_context"] = len(context) > 0
        if len(context) == 0:
            errors.append("Task should have context from previous requests")
    
    # Overall pass/fail
    passed = len(errors) == 0 and all(assertions.values())
    
    return assertions, passed, errors


async def run_multitask_session_tests(session_id, client, run_dir):
    """Run all multi-task tests for a single session."""
    print(f"\n[{session_id}] Starting multi-task session tests...")
    
    tests = get_multitask_tests_by_session(session_id)
    results = []
    all_step_ids = set()
    
    session_start = time.time()
    
    for i, test in enumerate(tests, 1):
        test_start = time.time()
        
        print(f"[{session_id}] Running test {i}/{len(tests)}: {test['name']}")
        
        # Send request
        response = await send_multitask_request(client, session_id, test["text"])
        
        # Small delay to allow queue processing
        await asyncio.sleep(0.1)
        
        # Get queue status after processing
        queue_status = await get_queue_status(client, session_id)
        
        test_duration = time.time() - test_start
        
        # Validate response
        if not response.get("success"):
            result = {
                "test_id": test["id"],
                "test_name": test["name"],
                "text": test["text"],
                "error": response.get("error"),
                "passed": False,
                "duration": test_duration
            }
            print(f"[{session_id}] Test {test['id']}: ✗ ({test_duration:.2f}s) - {response.get('error')}")
        else:
            assertions, passed, errors = validate_multitask_response(response, test, all_step_ids)
            
            result = {
                "test_id": test["id"],
                "test_name": test["name"],
                "text": test["text"],
                "expected_task_count": test.get("expected_task_count", 1),
                "actual_task_count": response.get("count", 0),
                "response": response.get("tasks", []),
                "queue_status": queue_status.get("status", {}),
                "assertions": assertions,
                "errors": errors,
                "passed": passed,
                "duration": test_duration
            }
            
            status = "✓" if passed else "✗"
            error_msg = f" - {errors[0]}" if errors else ""
            print(f"[{session_id}] Test {test['id']}: {status} ({test_duration:.2f}s){error_msg}")
        
        results.append(result)
    
    session_duration = time.time() - session_start
    
    # Calculate summary
    passed_count = sum(1 for r in results if r.get("passed", False))
    total_count = len(results)
    
    print(f"[{session_id}] Completed: {passed_count}/{total_count} passed ({session_duration:.2f}s)\n")
    
    # Save session results
    session_file = run_dir / f"{session_id}.json"
    with open(session_file, "w") as f:
        json.dump({
            "session_id": session_id,
            "total_tests": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count,
            "duration": session_duration,
            "tests": results
        }, f, indent=2)
    
    return {
        "session_id": session_id,
        "total": total_count,
        "passed": passed_count,
        "duration": session_duration,
        "results": results
    }


async def run_all_multitask_tests():
    """Run all multi-task tests across all sessions."""
    run_dir = get_next_run_dir()
    
    print("=" * 60)
    print("PLANNER AGENT MULTI-TASK TEST SUITE")
    print("=" * 60)
    print()
    
    # Check server health
    print("Checking server health...")
    if not await check_server_health():
        print("❌ Server is not responding. Please start the server:")
        print("   python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000")
        return None
    print("✓ Server is healthy\n")
    
    session_ids = get_multitask_session_ids()
    all_tests = get_all_multitask_tests()
    
    print(f"Running {len(all_tests)} tests across {len(session_ids)} sessions...")
    print(f"Sessions will run in parallel, tests within sessions run sequentially.")
    print(f"Results will be saved to: {run_dir.name}/\n")
    
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        # Run sessions in parallel
        session_tasks = [
            run_multitask_session_tests(sid, client, run_dir)
            for sid in session_ids
        ]
        session_summaries = await asyncio.gather(*session_tasks)
    
    total_duration = time.time() - start_time
    
    # Calculate overall summary
    total_tests = sum(s["total"] for s in session_summaries)
    total_passed = sum(s["passed"] for s in session_summaries)
    total_failed = total_tests - total_passed
    
    # Generate summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
        "duration": total_duration,
        "sessions": session_summaries
    }
    
    # Save summary
    summary_file = run_dir / "summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("=" * 60)
    print("MULTI-TASK TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests:       {total_tests}")
    print(f"Passed:            {total_passed} ({summary['pass_rate']:.1f}%)")
    print(f"Failed:            {total_failed}")
    print(f"Duration:          {total_duration:.2f}s")
    print(f"\nResults saved to: {run_dir}")
    print("=" * 60)
    
    print("\nPer-Session Results:")
    for s in session_summaries:
        status = "✓" if s["passed"] == s["total"] else "✗"
        print(f"  {status} {s['session_id']}: {s['passed']}/{s['total']} passed")
    
    if total_passed == total_tests:
        print("\n🎉 All multi-task tests passed!\n")
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Check results for details.\n")
    
    print("=" * 60)
    
    return summary


async def main():
    """Main entry point."""
    try:
        summary = await run_all_multitask_tests()
        if summary is None:
            exit(1)
        
        # Exit with error code if tests failed
        if summary["failed"] > 0:
            exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())

