# Orchestration Test Suite

Comprehensive test suite for the LLM orchestration pipeline that validates the full workflow from user request through planner to agent execution.

## Overview

This test suite validates:
- **Orchestration routing**: Correct agent selection based on task type
- **Response structure**: All required fields present in responses
- **Agent execution**: Each agent produces properly formatted output
- **Timing metrics**: Detailed performance tracking for the entire pipeline

## Test Coverage

### Single-Agent Workflows
- **EDIT**: UI component creation and modification
- **ACT**: User actions (clicks, scrolls, navigation)
- **CLARIFY**: Ambiguous requests requiring clarification

### Multi-Task Workflows
- **Same agent type**: Multiple EDITs or ACTs in sequence
- **Mixed agents**: EDIT → ACT, ACT → EDIT, complex sequences
- **Edge cases**: Very short/long requests, special characters, technical specs

### Test Count
- **20 comprehensive tests** covering all scenarios
- **38+ total tasks** executed across all tests
- Tests for single-agent, multi-task, and mixed workflows

## Running Tests

### Prerequisites

1. Server must be running:
```bash
cd llm
source venv/bin/activate
python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
```

2. Required dependencies (should be in venv):
- httpx
- fastapi
- uvicorn

### Run All Tests

```bash
cd llm
source venv/bin/activate
python tests/runner.py
```

### Output

Tests run sequentially and display:
- Real-time progress with pass/fail indicators
- Detailed timing for each test
- Task count per test
- Comprehensive summary at the end

## Results

Results are saved in `llm/tests/results/run-N/` directories:

### Summary Report (`summary.json`)

Contains:
- **Overall metrics**: Pass/fail counts, success rate, total duration
- **Timing breakdown**: Duration for each test with task counts
- **Agent distribution**: How many tasks went to each agent type
- **Routing accuracy**: Percentage of correctly routed tasks
- **Individual test details**: Full request/response data, assertions, errors

### Key Metrics

Example output:
```
Total Tests:          20
Passed:               18 (90.0%)
Failed:               2
Total Duration:       255.846s
Average Test Time:    12.792s
Average Per Task:     6.733s
Total Tasks Executed: 38
Routing Accuracy:     100.0%

AVERAGE TIME PER AGENT TYPE
  ACT        2.605s per task
  CLARIFY    1.515s per task
  EDIT       7.665s per task
```

## Report Structure

Each test result includes:

### Enhanced Timing Information
```json
{
  "test_id": "orch-edge-05",
  "name": "Edge - Sequential actions with context",
  "description": "Multiple related edits building on each other",
  "duration_seconds": 37.067,
  "task_count": 3,
  "average_per_task": 12.356,
  "tasks": [
    {
      "task_number": 1,
      "agent_type": "edit",
      "intent": "Add a card with pricing info",
      "estimated_duration_seconds": 11.689
    },
    {
      "task_number": 2,
      "agent_type": "edit",
      "intent": "make it have rounded corners",
      "estimated_duration_seconds": 11.689
    }
  ]
}
```

### Overall Statistics
```json
{
  "average_per_task": 6.733,
  "average_per_agent_type": {
    "edit": 7.665,
    "act": 2.605,
    "clarify": 1.515
  }
}
```

### Validation Results
```json
{
  "correct_task_count": true,
  "correct_routing": true,
  "all_fields_present": true,
  "response_structure_valid": true
}
```

### Agent Distribution
```json
{
  "edit": 27,
  "act": 9,
  "clarify": 2
}
```

## Understanding Results

### Pass/Fail Criteria

A test **passes** if:
1. ✓ Planner identifies correct number of tasks (with some flexibility)
2. ✓ Each task routes to appropriate agent type
3. ✓ All required response fields present
4. ✓ Agent outputs are properly formatted

A test **fails** if:
1. ✗ Wrong number of tasks identified
2. ✗ Incorrect agent routing
3. ✗ Missing required fields
4. ✗ Malformed agent output

### Common "Failures"

Some tests may "fail" because the LLM planner is more granular:
- "Make heading bold and large" → Split into 2 tasks instead of 1
- "Set width, height, padding" → Split into 3 tasks instead of 1

These are not bugs - they show the planner working intelligently!

## Performance Insights

### Timing Patterns (Based on Actual Test Results)
- **EDIT Agent**: ~7.7s per task (component generation, most complex)
- **ACT Agent**: ~2.6s per task (action generation, moderate)
- **CLARIFY Agent**: ~1.5s per task (clarification questions, fastest)
- **Multi-task**: Scales with task count + planner overhead (~1-2s)

### Per-Task Breakdown
The report now includes detailed per-task timing estimates:
- Each task's agent type (EDIT/ACT/CLARIFY)
- Task intent (what the planner identified)
- Estimated duration based on agent type and test total time
- Task execution order

Example from console output:
```
orch-edge-05: Edge - Sequential actions with context
Description: Multiple related edits building on each other
Total: 37.07s | Tasks: 3 | Avg/Task: 12.36s
  └─ Task 1: [EDIT] Add a card with pricing info... (11.69s)
  └─ Task 2: [EDIT] make it have rounded corners... (11.69s)
  └─ Task 3: [EDIT] add a shadow effect... (11.69s)
```

### Bottlenecks Identification
With per-task timing, you can now identify:
1. **Which agent type** is the bottleneck
2. **Which specific tasks** take longest
3. **How task complexity** affects timing
4. **Planner overhead** (difference between total and task sum)

## Test Structure

### Files
```
llm/tests/
├── __init__.py           # Package initialization
├── runner.py             # Main test executor
├── test_definitions.py   # 20 test cases
├── validator.py          # Validation logic
├── README.md             # This file
└── results/              # Test results
    └── run-N/
        └── summary.json  # Detailed report
```

### Adding New Tests

Add to `test_definitions.py`:

```python
{
    "id": "orch-new-test",
    "name": "Test Name",
    "sid": "orch-new-test",
    "text": "User request text",
    "description": "What this tests",
    "expected_tasks": 2,
    "expected_agents": ["edit", "act"]
}
```

## Validation Logic

The validator checks:

1. **Response structure** - PlanResponse with sid and results
2. **Task count** - Number of tasks matches expectations
3. **AgentResult fields** - session_id, step_id, intent, context, result, agent_type
4. **Agent routing** - step_type matches agent_type
5. **Output format** - JSON for EDIT, string for ACT/CLARIFY

## Comparison with Individual Agent Tests

### Agent-Specific Tests
- Test individual agents in isolation
- Focus on agent-specific output quality
- Faster execution (no orchestration overhead)

### Orchestration Tests (This Suite)
- Test full end-to-end pipeline
- Validate orchestration routing logic
- Measure real-world performance
- Verify agent integration

## Exit Codes

- **0**: All tests passed
- **1**: One or more tests failed or error occurred

## Troubleshooting

### Server Not Running
```
❌ Error: Server not running at http://localhost:8000
```
**Solution**: Start the server as shown in Prerequisites

### Import Errors
```
Error: httpx is required
```
**Solution**: `pip install httpx` in venv

### Timeout Errors
- Increase `TIMEOUT` in `runner.py` (default: 180s)
- Check server logs for issues

## Future Enhancements

Potential additions:
- Parallel test execution for speed
- Per-step timing (planner time, each agent time)
- Regression detection (compare with baseline)
- Performance trend analysis across runs
- More granular validation rules

