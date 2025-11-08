"""
Validation logic for clarifier agent test results.
Performs deterministic JSON structure checks and tracks LLM quality metrics.
"""

import uuid


def validate_response_structure(response):
    """Validate response has all required fields."""
    required_fields = ["session_id", "step_id", "intent", "context", "reply"]
    assertions = {}
    
    for field in required_fields:
        assertions[f"has_{field}"] = field in response
    
    return assertions


def validate_step_id_format(step_id):
    """Validate step_id is a valid UUID format."""
    try:
        uuid.UUID(step_id)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


def validate_field_types(response):
    """Validate all fields are strings."""
    assertions = {}
    
    fields = ["session_id", "step_id", "intent", "context", "reply"]
    for field in fields:
        if field in response:
            assertions[f"{field}_is_string"] = isinstance(response[field], str)
        else:
            assertions[f"{field}_is_string"] = False
    
    return assertions


def validate_reply_content(reply):
    """Validate reply is non-empty and has meaningful length."""
    assertions = {}
    
    assertions["reply_non_empty"] = reply is not None and len(str(reply).strip()) > 0
    assertions["reply_meaningful_length"] = len(str(reply).strip()) >= 10
    
    return assertions


def validate_reply_quality(reply, context, intent):
    """
    Track LLM quality metrics (not pass/fail, just tracked).
    These metrics help evaluate if the clarifier is asking good questions.
    """
    quality_metrics = {}
    
    # Check if reply references context
    reply_lower = reply.lower() if reply else ""
    context_lower = context.lower() if context else ""
    
    # Simple heuristic: does reply mention words from context?
    context_words = set(context_lower.split()) if context_lower else set()
    reply_words = set(reply_lower.split()) if reply_lower else set()
    
    common_words = {"the", "a", "an", "to", "and", "or", "in", "on", "at", "of", "for"}
    context_meaningful = context_words - common_words
    reply_meaningful = reply_words - common_words
    
    overlap = len(context_meaningful & reply_meaningful)
    quality_metrics["reply_references_context"] = overlap > 0
    quality_metrics["context_words_in_reply"] = overlap
    
    # Check if reply asks a clear question (contains question mark)
    quality_metrics["reply_asks_question"] = "?" in reply_lower
    
    # Check for Jarvis-style phrases
    jarvis_phrases = [
        "got it",
        "alright",
        "just to make sure",
        "let me get this straight",
        "quick clarification",
        "which one",
        "which",
        "clarify",
        "need to know"
    ]
    
    jarvis_present = any(phrase in reply_lower for phrase in jarvis_phrases)
    quality_metrics["jarvis_personality_present"] = jarvis_present
    
    return quality_metrics


def run_all_validations(test_case, response):
    """
    Run all validation checks for a test case.
    Returns: (assertions, passed, errors, quality_metrics)
    """
    assertions = {}
    errors = []
    
    # Structure validation
    structure = validate_response_structure(response)
    assertions.update(structure)
    
    if not all(structure.values()):
        missing = [field for field, present in structure.items() if not present]
        errors.append(f"Missing required fields: {', '.join(missing)}")
    
    # Session ID validation - check it matches the input
    expected_session_id = test_case.get("session_id", "")
    actual_session_id = response.get("session_id", "")
    assertions["session_id_matches_input"] = (actual_session_id == expected_session_id)
    
    if not assertions["session_id_matches_input"]:
        errors.append(f"Session ID mismatch: expected '{expected_session_id}', got '{actual_session_id}'")
    
    # Step ID validation - check it matches the input
    # Note: Clarifier doesn't generate step_id, it just echoes it back from the request
    expected_step_id = test_case.get("step_id", "")
    actual_step_id = response.get("step_id", "")
    assertions["step_id_matches_input"] = (actual_step_id == expected_step_id)
    
    if not assertions["step_id_matches_input"]:
        errors.append(f"Step ID mismatch: expected '{expected_step_id}', got '{actual_step_id}'")
    
    # Intent validation - check it matches the input (should be echoed back)
    expected_intent = test_case.get("intent", "")
    actual_intent = response.get("intent", "")
    assertions["intent_matches_input"] = (actual_intent == expected_intent)
    
    if not assertions["intent_matches_input"]:
        errors.append(f"Intent mismatch: expected '{expected_intent[:50]}...', got '{actual_intent[:50]}...'")
    
    # Context validation - check it matches the input (should be echoed back)
    expected_context = test_case.get("context", "")
    actual_context = response.get("context", "")
    assertions["context_matches_input"] = (actual_context == expected_context)
    
    if not assertions["context_matches_input"]:
        errors.append(f"Context mismatch: expected '{expected_context[:50]}...', got '{actual_context[:50]}...'")
    
    # Type validation
    type_checks = validate_field_types(response)
    assertions.update(type_checks)
    
    non_string_fields = [field for field, is_string in type_checks.items() if not is_string]
    if non_string_fields:
        errors.append(f"Non-string fields: {', '.join(non_string_fields)}")
    
    # Reply content validation
    reply = response.get("reply", "")
    reply_checks = validate_reply_content(reply)
    assertions.update(reply_checks)
    
    if not reply_checks.get("reply_non_empty"):
        errors.append("Reply is empty")
    
    if not reply_checks.get("reply_meaningful_length"):
        errors.append("Reply is too short (< 10 characters)")
    
    # Quality metrics (tracked but don't affect pass/fail)
    context = response.get("context", "")
    intent = response.get("intent", "")
    quality_metrics = validate_reply_quality(reply, context, intent)
    
    # Determine if test passed (all critical assertions true)
    critical_checks = [
        "has_session_id",
        "has_step_id",
        "has_intent",
        "has_context",
        "has_reply",
        "session_id_matches_input",
        "step_id_matches_input",
        "intent_matches_input",
        "context_matches_input",
        "session_id_is_string",
        "step_id_is_string",
        "intent_is_string",
        "context_is_string",
        "reply_is_string",
        "reply_non_empty",
        "reply_meaningful_length"
    ]
    
    passed = all(assertions.get(check, False) for check in critical_checks)
    
    return assertions, passed, errors, quality_metrics


def generate_test_summary(test_id, test_name, description, input_data, response, assertions, passed, errors, quality_metrics, duration):
    """Generate summary for a single test."""
    return {
        "test_id": test_id,
        "name": test_name,
        "description": description,
        "input": input_data,
        "response": response,
        "assertions": assertions,
        "quality_metrics": quality_metrics,
        "passed": passed,
        "errors": errors,
        "duration_seconds": round(duration, 2)
    }


def generate_overall_summary(test_results, total_duration):
    """Generate overall summary across all tests."""
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t.get("passed", False))
    failed_tests = total_tests - passed_tests
    
    # Calculate quality metrics averages
    total_context_refs = sum(
        1 for t in test_results 
        if t.get("quality_metrics", {}).get("reply_references_context", False)
    )
    
    total_questions = sum(
        1 for t in test_results 
        if t.get("quality_metrics", {}).get("reply_asks_question", False)
    )
    
    total_jarvis = sum(
        1 for t in test_results 
        if t.get("quality_metrics", {}).get("jarvis_personality_present", False)
    )
    
    summary = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
        "quality_metrics": {
            "replies_reference_context": f"{total_context_refs}/{total_tests} ({(total_context_refs/total_tests*100):.1f}%)" if total_tests > 0 else "N/A",
            "replies_ask_questions": f"{total_questions}/{total_tests} ({(total_questions/total_tests*100):.1f}%)" if total_tests > 0 else "N/A",
            "jarvis_personality": f"{total_jarvis}/{total_tests} ({(total_jarvis/total_tests*100):.1f}%)" if total_tests > 0 else "N/A"
        },
        "total_duration_seconds": round(total_duration, 2),
        "tests": test_results
    }
    
    return summary

