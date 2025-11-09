"""
Validator for orchestration pipeline tests.
Validates routing, response structure, and agent outputs.
"""

import json


def validate_plan_response(response):
    """Validate basic PlanResponse structure."""
    if "sid" not in response:
        return False, "Missing 'sid' field in response"
    if "results" not in response:
        return False, "Missing 'results' field in response"
    if not isinstance(response["results"], list):
        return False, "'results' must be a list"
    return True, None


def validate_agent_result(result):
    """Validate AgentResult structure."""
    required_fields = ["session_id", "step_id", "intent", "context", "result", "agent_type"]
    
    for field in required_fields:
        if field not in result:
            return False, f"Missing required field: {field}"
    
    # Validate agent_type is one of the expected values
    valid_agents = ["edit", "act", "clarify"]
    if result["agent_type"] not in valid_agents:
        return False, f"Invalid agent_type: {result['agent_type']} (must be one of {valid_agents})"
    
    return True, None


def validate_edit_output(result_string):
    """Validate EDIT agent output is valid JSON."""
    try:
        component = json.loads(result_string)
        
        # Check for basic component structure (allowing the new AST-style envelope)
        top_level = component
        tree = None

        if isinstance(component, dict) and "tree" in component and isinstance(component["tree"], dict):
            tree = component["tree"]
        elif isinstance(component, dict) and "component" in component and isinstance(component["component"], dict):
            tree = component["component"]

        # Choose the node we will validate (prefer the tree/component payload when present)
        node = tree or top_level

        if "id" not in node:
            return False, "EDIT output missing 'id' field"
        if "type" not in node:
            return False, "EDIT output missing 'type' field"
        if "props" not in node:
            return False, "EDIT output missing 'props' field"
        
        return True, None
    except json.JSONDecodeError as e:
        return False, f"EDIT output is not valid JSON: {e}"


def validate_act_output(result_string):
    """Validate ACT agent output is non-empty string."""
    if not result_string or not isinstance(result_string, str):
        return False, "ACT output must be a non-empty string"
    if len(result_string.strip()) == 0:
        return False, "ACT output is empty"
    return True, None


def validate_clarify_output(result_string):
    """Validate CLARIFY agent output is non-empty string."""
    if not result_string or not isinstance(result_string, str):
        return False, "CLARIFY output must be a non-empty string"
    if len(result_string.strip()) == 0:
        return False, "CLARIFY output is empty"
    return True, None


def run_all_validations(test, response, test_duration=0):
    """
    Run all validations for an orchestration test case.
    
    Returns:
        assertions: dict of validation results
        passed: bool indicating if test passed
        errors: list of error messages
        metrics: dict of quality metrics
    """
    assertions = {}
    passed = True
    errors = []
    metrics = {}
    
    # 1. Validate PlanResponse structure
    response_valid, response_error = validate_plan_response(response)
    assertions["response_structure_valid"] = response_valid
    
    if not response_valid:
        passed = False
        errors.append(f"Response structure: {response_error}")
        return assertions, passed, errors, metrics
    
    # 2. Validate task count
    results = response["results"]
    expected_tasks = test.get("expected_tasks", 1)
    actual_tasks = len(results)
    assertions["correct_task_count"] = actual_tasks == expected_tasks
    metrics["expected_tasks"] = expected_tasks
    metrics["actual_tasks"] = actual_tasks
    
    if actual_tasks != expected_tasks:
        errors.append(f"Task count mismatch: expected {expected_tasks}, got {actual_tasks}")
        passed = False
    
    # 3. Extract detailed task information
    task_details = []
    
    # 3. Validate each AgentResult
    assertions["all_results_valid"] = True
    for idx, result in enumerate(results):
        result_valid, result_error = validate_agent_result(result)
        assertions[f"result_{idx}_valid"] = result_valid
        
        if not result_valid:
            assertions["all_results_valid"] = False
            passed = False
            errors.append(f"Result {idx}: {result_error}")
            continue
        
        # Extract task details
        agent_type = result["agent_type"]
        intent = result.get("intent", "")
        
        # Extract meaningful intent (first part before |)
        intent_short = intent.split("|")[0].strip() if "|" in intent else intent[:80]
        
        task_detail = {
            "task_number": idx + 1,
            "agent_type": agent_type,
            "intent": intent_short,
            "step_id": result.get("step_id", ""),
        }
        task_details.append(task_detail)
        
        # 4. Validate agent routing
        expected_agents = test.get("expected_agents", [])
        
        if idx < len(expected_agents):
            expected_agent = expected_agents[idx]
            assertions[f"result_{idx}_correct_agent"] = agent_type == expected_agent
            
            if agent_type != expected_agent:
                # Allow some flexibility for clarify vs edit
                if not (agent_type == "clarify" and expected_agent == "edit"):
                    errors.append(f"Result {idx}: expected agent '{expected_agent}', got '{agent_type}'")
                    passed = False
        
        # 5. Validate agent-specific output format
        result_string = result["result"]
        
        if agent_type == "edit":
            output_valid, output_error = validate_edit_output(result_string)
            assertions[f"result_{idx}_output_valid"] = output_valid
            if not output_valid:
                errors.append(f"Result {idx} (EDIT): {output_error}")
                passed = False
        
        elif agent_type == "act":
            output_valid, output_error = validate_act_output(result_string)
            assertions[f"result_{idx}_output_valid"] = output_valid
            if not output_valid:
                errors.append(f"Result {idx} (ACT): {output_error}")
                passed = False
        
        elif agent_type == "clarify":
            output_valid, output_error = validate_clarify_output(result_string)
            assertions[f"result_{idx}_output_valid"] = output_valid
            if not output_valid:
                errors.append(f"Result {idx} (CLARIFY): {output_error}")
                passed = False
    
    # 6. Routing correctness summary
    correct_routing = all(
        assertions.get(f"result_{i}_correct_agent", True)
        for i in range(len(results))
    )
    assertions["correct_routing"] = correct_routing
    metrics["correct_routing"] = correct_routing
    
    # 7. All fields present summary
    all_fields_present = assertions.get("all_results_valid", False)
    assertions["all_fields_present"] = all_fields_present
    metrics["all_fields_present"] = all_fields_present
    
    # 8. Agent distribution
    agent_distribution = {}
    for result in results:
        agent_type = result.get("agent_type", "unknown")
        agent_distribution[agent_type] = agent_distribution.get(agent_type, 0) + 1
    metrics["agent_distribution"] = agent_distribution
    
    # 9. Task details for reporting
    metrics["task_details"] = task_details
    
    # 10. Extract real timing data if available
    timing_data = response.get("timing", {})
    if timing_data:
        metrics["planner_time_seconds"] = timing_data.get("planner_time_seconds", 0)
        metrics["total_agent_time_seconds"] = timing_data.get("total_agent_time_seconds", 0)
        metrics["orchestrator_overhead_seconds"] = round(
            timing_data.get("total_time_seconds", test_duration) - 
            timing_data.get("planner_time_seconds", 0) - 
            timing_data.get("total_agent_time_seconds", 0), 
            3
        )
        
        # Map real timing to tasks
        task_timings_map = {}
        for task_timing in timing_data.get("task_timings", []):
            task_timings_map[task_timing["step_id"]] = task_timing["duration_seconds"]
        
        # Add real timing to task details
        for task in task_details:
            step_id = task.get("step_id")
            if step_id in task_timings_map:
                task["actual_duration_seconds"] = task_timings_map[step_id]
            else:
                # Fallback: check if result has execution_time
                for result in results:
                    if result.get("step_id") == step_id:
                        task["actual_duration_seconds"] = result.get("execution_time_seconds", 0)
                        break
    else:
        # Fallback to estimates if no timing data available
        if actual_tasks > 0 and test_duration > 0:
            estimated_times = {"edit": 5.0, "act": 2.5, "clarify": 1.8}
            total_estimated = sum(estimated_times.get(t["agent_type"], 3.0) for t in task_details)
            planner_overhead = min(2.0, test_duration * 0.1)
            available_time = test_duration - planner_overhead
            
            for task in task_details:
                estimated = estimated_times.get(task["agent_type"], 3.0)
                task["estimated_duration_seconds"] = round((estimated / total_estimated) * available_time, 3)
    
    return assertions, passed, errors, metrics


def generate_test_summary(test_id, name, description, input_data, response, 
                          assertions, passed, errors, metrics, duration):
    """Generate a comprehensive test summary."""
    return {
        "test_id": test_id,
        "name": name,
        "description": description,
        "passed": passed,
        "input": input_data,
        "response": response,
        "assertions": assertions,
        "errors": errors,
        "metrics": metrics,
        "duration_seconds": round(duration, 3)
    }


def generate_overall_summary(test_results, total_duration):
    """Generate overall test run summary."""
    total_tests = len(test_results)
    passed = sum(1 for t in test_results if t.get("passed", False))
    failed = total_tests - passed
    success_rate = f"{(passed / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
    
    # Aggregate metrics
    total_tasks = sum(t.get("metrics", {}).get("actual_tasks", 0) for t in test_results)
    routing_successes = sum(1 for t in test_results if t.get("metrics", {}).get("correct_routing", False))
    
    # Agent distribution across all tests
    all_agents = {}
    for test in test_results:
        dist = test.get("metrics", {}).get("agent_distribution", {})
        for agent, count in dist.items():
            all_agents[agent] = all_agents.get(agent, 0) + count
    
    # Calculate average time per task
    total_task_time = sum(t["duration_seconds"] for t in test_results)
    average_per_task = round(total_task_time / total_tasks, 3) if total_tasks > 0 else 0
    
    # Calculate average per agent type using actual timing data
    agent_times = {}
    agent_counts = {}
    for test in test_results:
        task_details = test.get("metrics", {}).get("task_details", [])
        for task in task_details:
            agent = task["agent_type"]
            # Prefer actual timing over estimates
            duration = task.get("actual_duration_seconds", task.get("estimated_duration_seconds", 0))
            if duration > 0:
                agent_times[agent] = agent_times.get(agent, 0) + duration
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    average_per_agent = {
        agent: round(agent_times[agent] / agent_counts[agent], 3)
        for agent in agent_times if agent_counts.get(agent, 0) > 0
    }
    
    # Calculate planner timing statistics
    total_planner_time = sum(t.get("metrics", {}).get("planner_time_seconds", 0) for t in test_results)
    tests_with_timing = sum(1 for t in test_results if t.get("metrics", {}).get("planner_time_seconds", 0) > 0)
    average_planner_time = round(total_planner_time / tests_with_timing, 3) if tests_with_timing > 0 else 0
    
    # Enhanced timing breakdown with task details
    timing_by_test = []
    for t in test_results:
        task_details = t.get("metrics", {}).get("task_details", [])
        metrics = t.get("metrics", {})
        
        test_timing = {
            "test_id": t["test_id"],
            "name": t["name"],
            "description": t.get("description", ""),
            "duration_seconds": t["duration_seconds"],
            "task_count": metrics.get("actual_tasks", 0),
            "average_per_task": round(t["duration_seconds"] / max(1, metrics.get("actual_tasks", 1)), 3),
            "planner_time_seconds": metrics.get("planner_time_seconds", 0),
            "total_agent_time_seconds": metrics.get("total_agent_time_seconds", 0),
            "orchestrator_overhead_seconds": metrics.get("orchestrator_overhead_seconds", 0),
            "tasks": [
                {
                    "task_number": task["task_number"],
                    "agent_type": task["agent_type"],
                    "intent": task["intent"],
                    "duration_seconds": task.get("actual_duration_seconds", task.get("estimated_duration_seconds", 0))
                }
                for task in task_details
            ]
        }
        timing_by_test.append(test_timing)
    
    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "total_duration_seconds": round(total_duration, 3),
        "average_test_duration": round(total_duration / total_tests, 3) if total_tests > 0 else 0,
        "average_per_task": average_per_task,
        "average_per_agent_type": average_per_agent,
        "average_planner_time": average_planner_time,
        "total_planner_time": round(total_planner_time, 3),
        "total_tasks_executed": total_tasks,
        "routing_accuracy": f"{(routing_successes / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
        "agent_distribution": all_agents,
        "timing_breakdown": timing_by_test,
        "tests": test_results
    }

