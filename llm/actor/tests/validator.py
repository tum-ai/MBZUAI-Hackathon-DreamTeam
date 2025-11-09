"""
Validator utilities for actor agent tests.
Ensures actor responses, prompt generation, and session persistence behave as expected.
"""

from copy import deepcopy
from typing import Any, Dict, List, Tuple


REQUIRED_RESPONSE_FIELDS = {"session_id", "step_id", "intent", "context", "action"}


def validate_response_structure(response: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate the basic structure of an actor response."""
    missing = REQUIRED_RESPONSE_FIELDS.difference(response.keys())
    if missing:
        return False, f"Missing response field(s): {', '.join(sorted(missing))}"
    return True, ""


def validate_generate_action_call(test: Dict[str, Any], call_kwargs: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate the arguments passed to generate_action."""
    errors: List[str] = []

    expected_intent = test["intent"]
    if call_kwargs.get("intent") != expected_intent:
        errors.append(
            f"generate_action intent mismatch: expected '{expected_intent}', got '{call_kwargs.get('intent')}'"
        )

    expected_context = test["context"]
    if call_kwargs.get("context") != expected_context:
        errors.append(
            f"generate_action context mismatch: expected '{expected_context}', got '{call_kwargs.get('context')}'"
        )

    expected_prompt = test["mock_system_prompt"]
    if call_kwargs.get("system_prompt") != expected_prompt:
        errors.append("generate_action system_prompt mismatch")

    expected_snapshot = test.get("expected_dom_snapshot_for_prompt")
    actual_snapshot = call_kwargs.get("dom_snapshot")
    if expected_snapshot is not None and actual_snapshot != expected_snapshot:
        errors.append(
            "generate_action dom_snapshot argument mismatch "
            f"(expected={expected_snapshot!r}, actual={actual_snapshot!r})"
        )

    return len(errors) == 0, errors


def validate_session_save(
    test: Dict[str, Any],
    saved_sessions: List[Dict[str, Any]],
    response: Dict[str, Any],
) -> Tuple[bool, List[str]]:
    """Validate that session data was stored correctly."""
    if not saved_sessions:
        return False, ["save_session was not called"]

    latest = saved_sessions[-1]
    session_data = latest["data"]
    errors: List[str] = []

    if "actions" not in session_data:
        errors.append("Saved session missing 'actions' field")
        return False, errors

    actions = session_data["actions"]
    step_id = test["step_id"]

    if step_id not in actions:
        errors.append(f"Saved session missing action for step_id '{step_id}'")
    else:
        expected_entry = {
            "intent": test["intent"],
            "context": test["context"],
            "action": test["expected_action_output"],
        }
        saved_entry = actions[step_id]
        if saved_entry != expected_entry:
            errors.append(
                f"Saved action mismatch for step_id '{step_id}'. Expected {expected_entry}, got {saved_entry}"
            )

    expected_existing_ids = test.get("expected_existing_action_ids", [])
    for action_id in expected_existing_ids:
        if action_id not in actions:
            errors.append(f"Existing action '{action_id}' missing from saved session")

    return len(errors) == 0, errors


def run_all_validations(
    test: Dict[str, Any],
    response: Dict[str, Any],
    context: Dict[str, Any],
) -> Tuple[Dict[str, bool], bool, List[str]]:
    """Run all validations for a single actor test."""
    assertions: Dict[str, bool] = {}
    errors: List[str] = []
    passed = True

    structure_valid, structure_error = validate_response_structure(response)
    assertions["response_structure_valid"] = structure_valid
    if not structure_valid:
        passed = False
        errors.append(structure_error)
        return assertions, passed, errors

    expected_action = test["expected_action_output"]
    action_matches = response.get("action") == expected_action
    assertions["action_matches_expected"] = action_matches
    if not action_matches:
        passed = False
        errors.append(
            f"Response action mismatch: expected '{expected_action}', got '{response.get('action')}'"
        )

    generate_calls = context.get("generate_action_calls", [])
    assertions["generate_action_called_once"] = len(generate_calls) == 1
    if len(generate_calls) != 1:
        passed = False
        errors.append(f"generate_action expected 1 call, saw {len(generate_calls)}")
    else:
        _, kwargs = generate_calls[0]
        valid_generate, generate_errors = validate_generate_action_call(test, kwargs)
        assertions["generate_action_args_valid"] = valid_generate
        if not valid_generate:
            passed = False
            errors.extend(generate_errors)

    prompt_calls = context.get("get_system_prompt_calls", [])
    assertions["get_system_prompt_called_once"] = len(prompt_calls) == 1
    if len(prompt_calls) != 1:
        passed = False
        errors.append(f"get_system_prompt expected 1 call, saw {len(prompt_calls)}")
    else:
        prompt_args, _ = prompt_calls[0]
        expected_snapshot = test.get("expected_dom_snapshot_for_prompt")
        if expected_snapshot is not None:
            snapshot_passed = prompt_args[0] == expected_snapshot
            assertions["dom_snapshot_passed_to_prompt"] = snapshot_passed
            if not snapshot_passed:
                passed = False
                errors.append("get_system_prompt received unexpected dom_snapshot")

    fetch_calls = context.get("fetch_dom_snapshot_calls", [])
    expected_fetch_calls = 1
    assertions["fetch_dom_snapshot_invoked"] = len(fetch_calls) >= 1
    if not fetch_calls:
        errors.append("fetch_dom_snapshot was not invoked")
        passed = False

    session_valid, session_errors = validate_session_save(test, context.get("saved_sessions", []), response)
    assertions["session_persistence_valid"] = session_valid
    if not session_valid:
        passed = False
        errors.extend(session_errors)

    assertions["load_session_called"] = bool(context.get("load_session_calls"))
    if not assertions["load_session_called"]:
        passed = False
        errors.append("load_session was not called")

    return assertions, passed, errors


def generate_test_summary(
    test: Dict[str, Any],
    response: Dict[str, Any],
    assertions: Dict[str, bool],
    passed: bool,
    errors: List[str],
    duration_seconds: float,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """Create a structured summary for a single test run."""
    return {
        "test_id": test["id"],
        "name": test["name"],
        "intention": test["intent"],
        "input": {
            "session_id": test["session_id"],
            "step_id": test["step_id"],
            "intent": test["intent"],
            "context": test["context"],
        },
        "response": deepcopy(response),
        "assertions": assertions,
        "passed": passed,
        "errors": errors,
        "duration_seconds": round(duration_seconds, 3),
        "context": {
            "generate_action_call_count": len(context.get("generate_action_calls", [])),
            "save_session_call_count": len(context.get("saved_sessions", [])),
        },
    }


def generate_overall_summary(test_results: List[Dict[str, Any]], duration_seconds: float) -> Dict[str, Any]:
    """Generate high-level summary for all actor tests."""
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result.get("passed"))
    failed_tests = total_tests - passed_tests

    return {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests else "0.0%",
        "total_duration_seconds": round(duration_seconds, 2),
        "tests": test_results,
    }

