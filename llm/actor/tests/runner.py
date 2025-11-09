"""
Test runner for the actor agent.
These tests execute the actor pipeline with controlled mocks to avoid external dependencies.
"""

import asyncio
import json
import time
from copy import deepcopy
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from llm.actor.actor import process_action_request
from llm.actor.models import ActionRequest
from llm.actor.tests.test_definitions import get_all_tests
from llm.actor.tests.validator import (
    generate_overall_summary,
    generate_test_summary,
    run_all_validations,
)


RESULTS_DIR = Path(__file__).resolve().parent / "results"


def ensure_results_dir() -> None:
    """Ensure results directory exists."""
    RESULTS_DIR.mkdir(exist_ok=True)


def get_test_run_dir() -> Path:
    """Create a new numbered results directory for this run."""
    ensure_results_dir()

    existing_runs = [
        d for d in RESULTS_DIR.iterdir() if d.is_dir() and d.name.startswith("run-")
    ]
    run_number = 1
    if existing_runs:
        numbers: List[int] = []
        for entry in existing_runs:
            try:
                numbers.append(int(entry.name.split("-")[1]))
            except (IndexError, ValueError):
                continue
        if numbers:
            run_number = max(numbers) + 1

    run_dir = RESULTS_DIR / f"run-{run_number}"
    run_dir.mkdir(exist_ok=True)
    return run_dir


def make_async_fetch_mock(test_case: Dict[str, Any]) -> AsyncMock:
    """Create a mock for fetch_dom_snapshot based on the test case."""
    if "snapshot_error" in test_case:
        return AsyncMock(side_effect=test_case["snapshot_error"])
    dom_snapshot = test_case.get("mock_dom_snapshot_response", {"snapshot": {}})
    return AsyncMock(return_value=deepcopy(dom_snapshot))


def make_load_session_mock(test_case: Dict[str, Any], load_calls: List[str]):
    """Create a stub for load_session that returns isolated copies."""

    def _load(session_id: str) -> Dict[str, Any]:
        load_calls.append(session_id)
        seed = deepcopy(test_case.get("seed_session", {"sid": session_id}))
        return seed

    return _load


def make_save_session_mock(saved_sessions: List[Dict[str, Any]]):
    """Create a stub for save_session that records inputs."""

    def _save(session_id: str, session_data: Dict[str, Any]) -> None:
        saved_sessions.append(
            {"session_id": session_id, "data": deepcopy(session_data)}
        )

    return _save


async def run_single_test(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single actor test with mocks."""
    print(f"\n--- Running {test_case['id']}: {test_case['name']} ---")
    start = time.time()

    fetch_mock = make_async_fetch_mock(test_case)
    get_prompt_mock = MagicMock(return_value=test_case["mock_system_prompt"])
    generate_mock = MagicMock(return_value=test_case["mock_action_output"])
    load_calls: List[str] = []
    saved_sessions: List[Dict[str, Any]] = []

    load_session_stub = make_load_session_mock(test_case, load_calls)
    save_session_stub = make_save_session_mock(saved_sessions)

    request_model = ActionRequest(
        session_id=test_case["session_id"],
        step_id=test_case["step_id"],
        intent=test_case["intent"],
        context=test_case["context"],
    )

    with patch("llm.server.fetch_dom_snapshot", fetch_mock):
        with patch("llm.server.get_system_prompt", get_prompt_mock):
            with patch("llm.actor.actor.generate_action", generate_mock):
                with patch("llm.actor.llm_client.generate_action", generate_mock):
                    with patch(
                        "llm.actor.actor.load_session", side_effect=load_session_stub
                    ):
                        with patch(
                            "llm.actor.actor.save_session",
                            side_effect=save_session_stub,
                        ):
                            try:
                                response_model = await process_action_request(
                                    request_model
                                )
                                response_dict = response_model.model_dump()
                            except Exception as exc:  # pragma: no cover - unexpected
                                duration = time.time() - start
                                print(
                                    f"❌ {test_case['id']} raised unexpected exception: {exc}"
                                )
                                return {
                                    "test_id": test_case["id"],
                                    "name": test_case["name"],
                                    "passed": False,
                                    "errors": [str(exc)],
                                    "duration_seconds": round(duration, 3),
                                }

    duration = time.time() - start

    context = {
        "fetch_dom_snapshot_calls": [call.args for call in fetch_mock.await_args_list],
        "get_system_prompt_calls": [
            (call.args, call.kwargs) for call in get_prompt_mock.call_args_list
        ],
        "generate_action_calls": [
            (call.args, call.kwargs) for call in generate_mock.call_args_list
        ],
        "load_session_calls": load_calls,
        "saved_sessions": saved_sessions,
    }

    assertions, passed, errors = run_all_validations(test_case, response_dict, context)

    status = "✓" if passed else "✗"
    print(f"{status} Completed in {duration:.2f}s")
    if errors:
        for error in errors:
            print(f"   • {error}")

    return generate_test_summary(
        test_case,
        response_dict,
        assertions,
        passed,
        errors,
        duration,
        context,
    )


async def run_all_tests() -> Dict[str, Any]:
    """Run all actor tests sequentially."""
    print("=" * 60)
    print("ACTOR AGENT TEST SUITE")
    print("=" * 60)

    tests = get_all_tests()
    if not tests:
        print("No tests defined.")
        return {}

    run_dir = get_test_run_dir()
    print(f"Results directory: {run_dir}")

    results: List[Dict[str, Any]] = []
    overall_start = time.time()

    for index, test_case in enumerate(tests, start=1):
        print(f"\nTest {index}/{len(tests)}")
        result = await run_single_test(deepcopy(test_case))
        results.append(result)

    overall_duration = time.time() - overall_start
    summary = generate_overall_summary(results, overall_duration)

    summary_file = run_dir / "summary.json"
    with open(summary_file, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed:      {summary['passed']}")
    print(f"Failed:      {summary['failed']}")
    print(f"Success:     {summary['success_rate']}")
    print(f"Duration:    {summary['total_duration_seconds']}s")
    print("=" * 60)

    failed = [result for result in results if not result.get("passed")]
    if failed:
        print("\nFailed Tests:")
        for item in failed:
            print(f"  ✗ {item['test_id']}: {item['name']}")
            for error in item.get("errors", []):
                print(f"    - {error}")
    else:
        print("\n🎉 All actor tests passed!")

    return summary


def main() -> None:
    """Entrypoint for CLI execution."""
    try:
        summary = asyncio.run(run_all_tests())
        if summary and summary.get("failed", 0) > 0:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
