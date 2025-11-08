"""
Validator for editor agent tests.
Validates response format and component structure.
"""

import json


def validate_response_format(response):
    """Validate basic response structure."""
    required_fields = ["session_id", "step_id", "intent", "context", "code"]
    
    for field in required_fields:
        if field not in response:
            return False, f"Missing required field: {field}"
    
    return True, None


def validate_component_structure(component_json):
    """Validate component JSON structure."""
    try:
        component = json.loads(component_json) if isinstance(component_json, str) else component_json
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    
    # Check required fields
    if "id" not in component:
        return False, "Component missing 'id' field"
    if "type" not in component:
        return False, "Component missing 'type' field"
    if "props" not in component:
        return False, "Component missing 'props' field"
    
    # Validate props is a dict
    if not isinstance(component["props"], dict):
        return False, "Component 'props' must be a dictionary"
    
    return True, None


def run_all_validations(test, response):
    """Run all validations for a test case."""
    assertions = {}
    passed = True
    errors = []
    quality_report = {}
    
    # Validate response format
    format_valid, format_error = validate_response_format(response)
    assertions["response_format_valid"] = format_valid
    
    if not format_valid:
        passed = False
        errors.append(f"Response format: {format_error}")
        return assertions, passed, errors, {}
    
    # Validate component structure
    code = response.get("code", "")
    struct_valid, struct_error = validate_component_structure(code)
    assertions["component_structure_valid"] = struct_valid
    
    if not struct_valid:
        passed = False
        errors.append(f"Component structure: {struct_error}")
        return assertions, passed, errors, {}
    
    # Parse component for comprehensive validation
    try:
        component = json.loads(code)
        
        # === COMPREHENSIVE COMPONENT VALIDATION ===
        
        # 1. Required Fields
        assertions["has_component_id"] = bool(component.get("id"))
        assertions["has_component_type"] = bool(component.get("type"))
        assertions["has_props"] = "props" in component
        assertions["has_slots"] = "slots" in component
        
        if not assertions["has_component_id"]:
            errors.append("Component missing 'id' field")
        if not assertions["has_component_type"]:
            errors.append("Component missing 'type' field")
        if not assertions["has_props"]:
            errors.append("Component missing 'props' field")
        
        # 2. Component Type Validation
        if test.get("expected_component"):
            expected = test["expected_component"].lower()
            actual = component.get("type", "").lower()
            assertions["component_type_matches"] = expected in actual or actual in expected
            if not assertions["component_type_matches"]:
                errors.append(f"Component type mismatch: expected '{expected}', got '{actual}'")
        
        # 3. ID Quality Check
        component_id = component.get("id", "")
        assertions["id_is_semantic"] = bool(component_id and "-" in component_id)
        quality_report["id"] = component_id
        
        # 4. Props Validation
        props = component.get("props", {})
        quality_report["props_count"] = len(props)
        
        # Check for text content
        if test.get("expected_text"):
            text_valid, text_error = validate_text_content(component, test["expected_text"])
            assertions["text_content_valid"] = text_valid
            if not text_valid:
                passed = False
                errors.append(text_error)
            
            # Get text from props or slots for quality report
            text_content = props.get("text") or props.get("content") or props.get("label")
            if not text_content and "slots" in component:
                slots = component["slots"]
                if isinstance(slots, dict):
                    for slot_content in slots.values():
                        if isinstance(slot_content, str):
                            text_content = slot_content
                            break
            quality_report["text_content"] = text_content or "N/A"
        
        # 5. Style Validation
        styles = props.get("style", {})
        quality_report["styles_count"] = len(styles)
        quality_report["has_styles"] = len(styles) > 0
        
        if len(styles) > 0:
            assertions["component_has_styles"] = True
            quality_report["styles"] = styles
            
            # Check for common style quality indicators
            style_quality_checks = {
                "has_spacing": any(k in styles for k in ["padding", "margin"]),
                "has_colors": any(k in styles for k in ["color", "backgroundColor", "background"]),
                "has_sizing": any(k in styles for k in ["width", "height", "fontSize"]),
                "has_layout": any(k in styles for k in ["display", "flexDirection", "justifyContent", "alignItems"])
            }
            quality_report["style_quality"] = style_quality_checks
        else:
            assertions["component_has_styles"] = False
        
        # Validate expected styles
        if test.get("expected_style"):
            style_valid, style_errors = validate_styles(component, test["expected_style"])
            assertions["styles_valid"] = style_valid
            if not style_valid:
                passed = False
                errors.extend(style_errors)
        
        # 6. Slots Validation
        slots = component.get("slots", {})
        quality_report["slots_count"] = len(slots)
        assertions["slots_structure_valid"] = isinstance(slots, dict)
        
        # 7. Events Validation (if present)
        if "events" in component:
            events = component["events"]
            assertions["has_events"] = True
            quality_report["events"] = list(events.keys()) if isinstance(events, dict) else []
        else:
            assertions["has_events"] = False
        
        # 8. Overall Quality Score
        quality_score = calculate_quality_score(component, test)
        quality_report["quality_score"] = quality_score
        assertions["quality_score_acceptable"] = quality_score >= 70  # 70% threshold
        
        # 9. Session/Step ID Validation
        assertions["session_id_matches"] = response.get("session_id") == test.get("session_id")
        assertions["step_id_matches"] = response.get("step_id") == test.get("step_id")
        
        # 10. Custom Props Validation
        if test.get("expected_props"):
            props_valid, props_errors = validate_component_props(component, test["expected_props"])
            assertions["props_valid"] = props_valid
            if not props_valid:
                passed = False
                errors.extend(props_errors)
        
    except json.JSONDecodeError as e:
        passed = False
        errors.append(f"Could not parse component JSON: {e}")
        return assertions, passed, errors, {}
    
    # Final pass/fail determination
    critical_assertions = [
        "response_format_valid",
        "component_structure_valid",
        "has_component_id",
        "has_component_type"
    ]
    
    for assertion in critical_assertions:
        if not assertions.get(assertion, False):
            passed = False
    
    return assertions, passed, errors, quality_report


def calculate_quality_score(component, test):
    """Calculate overall quality score for the generated component."""
    score = 0
    max_score = 100
    
    # ID quality (10 points)
    component_id = component.get("id", "")
    if component_id and "-" in component_id and len(component_id) > 3:
        score += 10
    elif component_id:
        score += 5
    
    # Props exist (10 points)
    props = component.get("props", {})
    if len(props) > 0:
        score += 10
    
    # Has styles (20 points)
    styles = props.get("style", {})
    if len(styles) > 0:
        score += 10
        # Style quality (additional 10 points)
        if len(styles) >= 3:  # At least 3 style properties
            score += 10
    
    # Text content (if expected) (20 points)
    if test.get("expected_text"):
        text_fields = ["text", "content", "label"]
        for field in text_fields:
            if field in props:
                expected = test["expected_text"].lower()
                actual = str(props[field]).lower()
                if expected in actual:
                    score += 20
                    break
    else:
        score += 10  # No text expected, so give partial credit
    
    # Component type correct (20 points)
    if test.get("expected_component"):
        expected = test["expected_component"].lower()
        actual = component.get("type", "").lower()
        if expected in actual or actual in expected:
            score += 20
        else:
            score += 5  # Partial credit if component exists
    else:
        score += 10
    
    # Slots structure (10 points)
    if "slots" in component and isinstance(component["slots"], dict):
        score += 10
    
    # Professional styling indicators (10 points)
    if styles:
        professional_indicators = ["padding", "margin", "fontSize", "borderRadius", "boxShadow"]
        present = sum(1 for ind in professional_indicators if ind in styles)
        score += min(10, present * 2)
    
    return min(score, max_score)


def validate_component_props(component, expected_props):
    """Validate component has expected properties."""
    errors = []
    
    props = component.get("props", {})
    
    for key, expected_value in expected_props.items():
        if key not in props:
            errors.append(f"Missing expected prop: {key}")
        elif expected_value is not None and props[key] != expected_value:
            errors.append(f"Prop '{key}' value mismatch: expected '{expected_value}', got '{props[key]}'")
    
    return len(errors) == 0, errors


def validate_text_content(component, expected_text):
    """Validate component contains expected text."""
    props = component.get("props", {})
    slots = component.get("slots", {})
    
    # Check in different possible text fields in props
    text_fields = ["text", "content", "label"]
    
    for field in text_fields:
        if field in props:
            actual_text = str(props[field]).lower()
            if expected_text.lower() in actual_text:
                return True, None
    
    # Also check in slots (for links and other components that put text in slots)
    if isinstance(slots, dict):
        for slot_name, slot_content in slots.items():
            if isinstance(slot_content, str):
                if expected_text.lower() in slot_content.lower():
                    return True, None
            elif isinstance(slot_content, list):
                for item in slot_content:
                    if isinstance(item, str) and expected_text.lower() in item.lower():
                        return True, None
                    elif isinstance(item, dict):
                        # Recursively check nested components
                        nested_result, _ = validate_text_content(item, expected_text)
                        if nested_result:
                            return True, None
    
    return False, f"Expected text '{expected_text}' not found in component"


def validate_styles(component, expected_styles):
    """Validate component has expected styles."""
    errors = []
    
    props = component.get("props", {})
    styles = props.get("style", {})
    
    if not styles:
        return False, ["Component has no styles"]
    
    for key, expected_value in expected_styles.items():
        if key not in styles:
            errors.append(f"Missing expected style: {key}")
        elif expected_value is not None and styles[key] != expected_value:
            # For some styles, just check they exist, not exact value
            pass
    
    return len(errors) == 0, errors


def generate_test_summary(test_id, name, description, input_data, response, assertions, passed, errors, quality_report, duration):
    """Generate summary for a single test."""
    return {
        "test_id": test_id,
        "name": name,
        "description": description,
        "input": input_data,
        "response": response,
        "assertions": assertions,
        "passed": passed,
        "errors": errors,
        "quality_report": quality_report,
        "duration_seconds": round(duration, 2)
    }


def generate_overall_summary(test_results, total_duration):
    """Generate overall summary for all tests."""
    total = len(test_results)
    passed = sum(1 for t in test_results if t.get("passed", False))
    failed = total - passed
    
    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
        "total_duration_seconds": round(total_duration, 2),
        "tests": test_results
    }

