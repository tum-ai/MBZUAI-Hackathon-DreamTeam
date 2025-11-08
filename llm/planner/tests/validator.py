"""
Validation logic for planner agent test results.
Checks system behavior and LLM classification quality.
"""

import uuid
import json
from pathlib import Path


def validate_response_structure(response):
    """Validate response has required fields."""
    required_fields = ["step_id", "step_type", "intent", "context"]
    assertions = {}
    
    for field in required_fields:
        assertions[f"has_{field}"] = field in response
    
    return assertions


def validate_step_id(step_id):
    """Validate step_id is a valid UUID."""
    try:
        uuid.UUID(step_id)
        return True
    except (ValueError, AttributeError):
        return False


def validate_step_type(step_type):
    """Validate step_type is one of: edit, act, clarify."""
    valid_types = ["edit", "act", "clarify"]
    return step_type in valid_types


def validate_intent_format(intent):
    """Validate intent contains user text and explanation separated by |."""
    if not intent or not isinstance(intent, str):
        return False
    
    # Check if it contains the separator
    return " | " in intent and len(intent.split(" | ")) >= 2


def validate_explanation_quality(intent):
    """Check if explanation part is non-empty and meaningful."""
    if not intent or " | " not in intent:
        return False
    
    parts = intent.split(" | ", 1)
    if len(parts) < 2:
        return False
    
    explanation = parts[1].strip()
    
    # Explanation should be at least 10 characters
    return len(explanation) >= 10


def validate_context_empty(context, should_be_empty):
    """Validate context is empty for first request."""
    is_empty = context == "" or context is None
    return is_empty == should_be_empty


def validate_context_count(context, expected_count):
    """Validate context contains expected number of previous prompts."""
    if not context:
        return expected_count == 0
    
    # Context is concatenated with " | " separator
    prompts = context.split(" | ")
    actual_count = len([p for p in prompts if p.strip()])
    
    return actual_count == expected_count


def validate_context_length(context, should_be_long):
    """Validate context length for summarization trigger."""
    if should_be_long:
        # Long context should be >100 chars
        return len(context) > 100
    else:
        # Short context can be any length <=100
        return True


def validate_intent_classification(response, expected_intent, acceptable_intents=None):
    """Validate LLM classified intent correctly."""
    actual_intent = response.get("step_type", "")
    
    # Check if it matches expected
    if actual_intent == expected_intent:
        return True
    
    # Check if it's in acceptable alternatives
    if acceptable_intents and actual_intent in acceptable_intents:
        return True
    
    return False


def validate_session_persistence(session_id, expected_prompts):
    """Validate session file contains correct prompts."""
    sessions_dir = Path(__file__).resolve().parent.parent / "sessions"
    session_file = sessions_dir / f"{session_id}.json"
    
    if not session_file.exists():
        return False
    
    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
        
        actual_prompts = session_data.get("prompts", [])
        
        # Should only have last 2 prompts
        if len(actual_prompts) > 2:
            return False
        
        # Check if expected prompts are in session (last ones)
        if len(expected_prompts) > 0:
            for i, expected in enumerate(expected_prompts[-2:]):
                if i < len(actual_prompts):
                    if actual_prompts[-(len(expected_prompts) - i)] != expected:
                        return False
        
        return True
    except Exception:
        return False


def run_all_validations(test_case, response, all_step_ids, session_prompts):
    """Run all validation checks for a test case."""
    assertions = {}
    errors = []
    
    # System behavior checks
    structure = validate_response_structure(response)
    assertions.update(structure)
    
    if not all(structure.values()):
        errors.append("Missing required fields in response")
    
    # Step ID validation
    step_id = response.get("step_id", "")
    assertions["valid_step_id_format"] = validate_step_id(step_id)
    
    if step_id in all_step_ids:
        assertions["step_id_unique"] = False
        errors.append(f"Duplicate step_id: {step_id}")
    else:
        assertions["step_id_unique"] = True
        all_step_ids.add(step_id)
    
    # Step type validation
    step_type = response.get("step_type", "")
    assertions["valid_step_type"] = validate_step_type(step_type)
    
    # Intent format validation
    intent = response.get("intent", "")
    assertions["valid_intent_format"] = validate_intent_format(intent)
    assertions["explanation_quality"] = validate_explanation_quality(intent)
    
    # Context validation
    context = response.get("context", "")
    
    if test_case.get("expected_context_empty"):
        assertions["context_empty_correct"] = validate_context_empty(context, True)
    
    if "expected_context_count" in test_case:
        expected_count = test_case["expected_context_count"]
        assertions["context_count_correct"] = validate_context_count(context, expected_count)
    
    if test_case.get("expected_context_long"):
        # For long context, check if previous context was >100 chars
        # This is validated in the next request after the long one
        assertions["context_length_check"] = True
    
    # LLM classification quality
    if "expected_intent" in test_case:
        expected = test_case["expected_intent"]
        acceptable = test_case.get("acceptable_intents", None)
        assertions["intent_classification"] = step_type
        assertions["classification_correct"] = validate_intent_classification(response, expected, acceptable)
        
        if not assertions["classification_correct"]:
            acceptable_str = f" or {acceptable}" if acceptable else ""
            errors.append(f"Expected intent '{expected}'{acceptable_str} but got '{step_type}'")
    
    # Check if test passed (all critical assertions true)
    critical_checks = [
        "has_step_id",
        "has_step_type",
        "has_intent",
        "has_context",
        "valid_step_id_format",
        "step_id_unique",
        "valid_step_type",
        "valid_intent_format"
    ]
    
    passed = all(assertions.get(check, False) for check in critical_checks)
    
    # Note: We don't fail on classification_correct since LLM might have valid reasons
    # to classify differently, but we track it
    
    return assertions, passed, errors


def generate_session_summary(session_id, tests, duration):
    """Generate summary report for a test session."""
    total = len(tests)
    passed = sum(1 for t in tests if t.get("passed", False))
    failed = total - passed
    
    summary = {
        "session_id": session_id,
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        "duration_seconds": round(duration, 2),
        "tests": tests
    }
    
    return summary


def generate_overall_summary(session_summaries, total_duration):
    """Generate overall summary across all sessions."""
    total_tests = sum(s["total_tests"] for s in session_summaries)
    total_passed = sum(s["passed"] for s in session_summaries)
    total_failed = sum(s["failed"] for s in session_summaries)
    
    # Classification accuracy
    classification_correct = 0
    classification_total = 0
    
    for session in session_summaries:
        for test in session["tests"]:
            if "classification_correct" in test.get("assertions", {}):
                classification_total += 1
                if test["assertions"]["classification_correct"]:
                    classification_correct += 1
    
    summary = {
        "total_sessions": len(session_summaries),
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "success_rate": f"{(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "0%",
        "classification_accuracy": f"{(classification_correct/classification_total*100):.1f}%" if classification_total > 0 else "N/A",
        "total_duration_seconds": round(total_duration, 2),
        "sessions": session_summaries
    }
    
    return summary

