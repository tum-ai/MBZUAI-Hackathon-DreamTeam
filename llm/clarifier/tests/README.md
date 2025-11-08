# Clarifier Agent Test Suite

Comprehensive test suite for the Clarifier Agent with 15 test cases covering diverse scenarios. Tests validate JSON structure deterministically while K2 Think Model evaluates response quality.

## Overview

The clarifier test suite validates two aspects of the clarifier agent:

1. **Deterministic Validation** (Pass/Fail): JSON structure, field types, UUID format, and content requirements
2. **Quality Metrics** (Tracked): Response quality evaluated by K2 Think Model - context references, question clarity, and Jarvis personality

## Test Coverage (15 Tests)

### Category 1: Ambiguous Pronouns (3 tests)
- **T01**: "Change that" with multiple previous actions
- **T02**: "Make it bigger" with logo and text context  
- **T03**: "Fix this" with navigation and button context

**Purpose**: Test clarifier's ability to identify and ask about ambiguous pronouns in different contexts.

### Category 2: Vague References (3 tests)
- **T04**: "Update the thing on top" with multiple header elements
- **T05**: "Modify the stuff in the middle section" with multiple content areas
- **T06**: "Adjust the element" with many form components

**Purpose**: Validate handling of vague, non-specific references to UI elements.

### Category 3: Missing Information (3 tests)
- **T07**: "Change the color" without specifying target element
- **T08**: "Resize" without target or dimensions
- **T09**: "Add a button" without position specification

**Purpose**: Test clarifier's ability to identify missing critical information.

### Category 4: Edge Cases (3 tests)
- **T10**: Conflicting context with contradictory previous changes
- **T11**: "Make it responsive" without specifying scope
- **T12**: Special characters in intent/context

**Purpose**: Validate handling of complex real-world scenarios and special characters.

### Category 5: Complex & Unrelated (3 tests)
- **T13**: Multiple ambiguous references in single request
- **T14**: Technical jargon ("WCAG AA compliance stuff") requiring clarification
- **T15**: Completely unrelated/nonsensical query

**Purpose**: Test robustness with complex requests and edge cases including nonsensical input.

## Running the Tests

### Prerequisites

1. **Server must be running** with both `/clarify` and `/health` endpoints:

```bash
cd /Users/georgychomakhashvili/MBZUAI-Hackathon-DreamTeam
./llm/venv/bin/python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
```

2. **Dependencies installed**:
   - httpx
   - asyncio
   - pydantic
   - openai

### Execute Tests

From the project root directory:

```bash
# Run all 15 tests in parallel
./llm/venv/bin/python -m llm.clarifier.tests.runner
```

Or with activated venv:

```bash
source llm/venv/bin/activate
python -m llm.clarifier.tests.runner
```

## Test Execution

- **All 15 tests run simultaneously** using `asyncio.gather()` for maximum efficiency
- Each test sends a POST request to `/clarify` endpoint
- Results are validated immediately upon response
- Total execution time typically 10-30 seconds depending on K2 Think Model latency

## Understanding Results

### Terminal Output

The test runner displays:

1. **Real-time progress**: Each test shows status as it completes
2. **Summary statistics**: Pass/fail counts and success rate
3. **Quality metrics**: K2 Think Model evaluation scores
4. **Failed tests**: Detailed error messages for any failures
5. **Sample replies**: First 3 clarification responses

### Result Files

Results are saved to `llm/clarifier/tests/results/run-N/`:

- **`summary.json`**: Complete test results with all data

#### Summary JSON Structure

```json
{
  "total_tests": 15,
  "passed": 15,
  "failed": 0,
  "success_rate": "100.0%",
  "quality_metrics": {
    "replies_reference_context": "14/15 (93.3%)",
    "replies_ask_questions": "15/15 (100.0%)",
    "jarvis_personality": "13/15 (86.7%)"
  },
  "total_duration_seconds": 24.5,
  "tests": [
    {
      "test_id": "T01",
      "name": "Ambiguous pronoun - 'that' with multiple actions",
      "description": "...",
      "input": {
        "session_id": "clarifier-test-01",
        "step_id": "step-01-ambiguous-that",
        "intent": "Change that | ...",
        "context": "..."
      },
      "response": {
        "session_id": "clarifier-test-01",
        "step_id": "step-01-ambiguous-that",
        "intent": "Change that | ...",
        "context": "...",
        "reply": "Got it, but which 'that' are we working with? ..."
      },
      "assertions": {
        "has_session_id": true,
        "has_step_id": true,
        "has_intent": true,
        "has_context": true,
        "has_reply": true,
        "valid_step_id_format": true,
        "session_id_is_string": true,
        "step_id_is_string": true,
        "intent_is_string": true,
        "context_is_string": true,
        "reply_is_string": true,
        "reply_non_empty": true,
        "reply_meaningful_length": true
      },
      "quality_metrics": {
        "reply_references_context": true,
        "context_words_in_reply": 3,
        "reply_asks_question": true,
        "jarvis_personality_present": true
      },
      "passed": true,
      "errors": [],
      "duration_seconds": 2.34
    }
  ]
}
```

## Validation Criteria

### Deterministic Checks (Must Pass)

These are strict requirements that determine pass/fail:

| Check | Requirement |
|-------|-------------|
| `has_session_id` | Response contains session_id field |
| `has_step_id` | Response contains step_id field |
| `has_intent` | Response contains intent field |
| `has_context` | Response contains context field |
| `has_reply` | Response contains reply field |
| `valid_step_id_format` | step_id is valid UUID format |
| `*_is_string` | All fields are string type |
| `reply_non_empty` | Reply has content |
| `reply_meaningful_length` | Reply is at least 10 characters |

**All deterministic checks must pass for test to pass.**

### Quality Metrics (Tracked, Not Pass/Fail)

These metrics evaluate response quality but don't fail tests:

| Metric | Meaning |
|--------|---------|
| `reply_references_context` | Reply mentions words from context |
| `context_words_in_reply` | Count of context words in reply |
| `reply_asks_question` | Reply contains question mark |
| `jarvis_personality_present` | Reply uses Jarvis-style phrases |

**Quality metrics are for K2 Think Model evaluation only.**

## Interpreting Results

### All Tests Pass (100%)

✅ **Excellent**: Clarifier properly validates JSON structure and generates responses.

Check quality metrics:
- **High context references (>80%)**: Clarifier is contextually aware
- **High question rate (>90%)**: Clarifier asks clear questions
- **High Jarvis personality (>70%)**: Maintains character consistency

### Some Tests Fail (<100%)

❌ **Issue**: Check failed test errors:

**Common failures:**
- Missing fields → Check ClarifyResponse model in `clarifier.py`
- Invalid UUID → Check step_id generation
- Empty replies → Check LLM client integration
- Type errors → Check response serialization

### Quality Metrics Low

⚠️ **Warning**: Tests pass but quality could be better:

- **Low context references (<50%)**: Replies may not reference previous actions adequately
- **Low question rate (<70%)**: Replies may not be asking clear questions
- **Low Jarvis personality (<50%)**: May lack personality or sound generic

**Note**: These don't fail tests but indicate areas for prompt improvement.

## Troubleshooting

### Server Not Running

```
❌ Error: Server not running at http://localhost:8000
```

**Solution**: Start the server:
```bash
cd /Users/georgychomakhashvili/MBZUAI-Hackathon-DreamTeam
./llm/venv/bin/python -m uvicorn llm.server:app --host 0.0.0.0 --port 8000
```

### Import Errors

```
ModuleNotFoundError: No module named 'httpx'
```

**Solution**: Install dependencies:
```bash
./llm/venv/bin/pip install httpx
```

### Timeout Errors

```
Error: Request timeout
```

**Solution**: K2 Think Model may be slow. Timeout is set to 120s in `runner.py`. If needed, increase `TIMEOUT` constant.

### All Tests Fail with Same Error

Check if the `/clarify` endpoint is properly integrated in `llm/server.py`:

```python
from llm.clarifier.clarifier import process_clarification_request
from llm.clarifier.models import ClarifyRequest

@app.post("/clarify")
async def clarify_endpoint(request: ClarifyRequest):
    response = process_clarification_request(request)
    return response
```

## Test Development

### Adding New Tests

1. Open `test_definitions.py`
2. Add test case to `CLARIFIER_TESTS` list:

```python
{
    "id": "T16",
    "name": "Your test name",
    "session_id": "clarifier-test-16",
    "step_id": "step-16-unique-id",
    "intent": "User request | Explanation of ambiguity",
    "context": "Previous action 1 | Previous action 2",
    "description": "What this test validates"
}
```

3. Run tests to validate new case

### Modifying Validation

Edit `validator.py` to add new checks:

```python
def validate_custom_check(response):
    # Your validation logic
    return True/False
```

Then add to `run_all_validations()` function.

## Architecture

```
llm/clarifier/tests/
├── __init__.py              # Package marker
├── test_definitions.py      # 15 test case definitions
├── validator.py             # Validation logic (deterministic + quality)
├── runner.py                # Test execution engine (parallel)
├── README.md                # This file
└── results/                 # Auto-generated test results
    ├── run-1/
    │   └── summary.json
    ├── run-2/
    │   └── summary.json
    └── ...
```

## Integration with CI/CD

Exit codes:
- **0**: All tests passed
- **1**: One or more tests failed or error occurred

Use in CI pipeline:

```bash
./llm/venv/bin/python -m llm.clarifier.tests.runner
if [ $? -eq 0 ]; then
    echo "Tests passed"
else
    echo "Tests failed"
    exit 1
fi
```

## Comparison with Planner Tests

| Aspect | Planner Tests | Clarifier Tests |
|--------|---------------|-----------------|
| Test count | 30 tests | 15 tests |
| Execution | 3 sessions (parallel), tests sequential within session | All tests in parallel |
| Focus | Intent classification, context management | Clarification quality, JSON structure |
| Validation | Classification accuracy, session state | Field validation, response quality |
| Session management | Tests share session state | Each test uses isolated session |

## Next Steps

1. **Run tests regularly** during clarifier development
2. **Monitor quality metrics** to ensure good clarification questions
3. **Add tests** for new edge cases as discovered
4. **Review sample replies** to evaluate Jarvis personality consistency

## Support

For issues or questions about the test suite:
1. Check this README
2. Review test results in `results/run-N/summary.json`
3. Examine individual test definitions in `test_definitions.py`
4. Validate server is running with `/clarify` endpoint

