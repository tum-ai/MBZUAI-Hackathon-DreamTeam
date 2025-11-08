"""
Multi-task test case definitions for planner agent queue system.
Tests the ability to split, queue, and process multiple tasks from a single request.
"""

MULTITASK_TEST_SESSIONS = {
    "multitask-a": {
        "name": "Basic Multi-Task Splitting",
        "tests": [
            {
                "id": "MT-A1",
                "name": "Simple three-task sequence",
                "text": "scroll down, click the submit button, and make it orange",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "scroll", "step_type": "act"},
                    {"contains": "click", "step_type": "act"},
                    {"contains": "orange", "step_type": "edit"}
                ],
                "description": "Classic multi-task example: 2 actions + 1 edit"
            },
            {
                "id": "MT-A2",
                "name": "Two-task action sequence",
                "text": "navigate to the pricing page and scroll to the comparison table",
                "expected_task_count": 2,
                "expected_tasks": [
                    {"contains": "navigate", "step_type": "act"},
                    {"contains": "scroll", "step_type": "act"}
                ],
                "description": "Two sequential actions"
            },
            {
                "id": "MT-A3",
                "name": "Two-task edit sequence",
                "text": "add a hero section with a title and then add a subtitle below it",
                "expected_task_count": 2,
                "expected_tasks": [
                    {"contains": "hero", "step_type": "edit"},
                    {"contains": "subtitle", "step_type": "edit"}
                ],
                "description": "Sequential edits with explicit 'then'"
            },
            {
                "id": "MT-A4",
                "name": "Mixed action-edit-action",
                "text": "scroll down, change the button color to blue, then click the menu",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "scroll", "step_type": "act"},
                    {"contains": "blue", "step_type": "edit"},
                    {"contains": "menu", "step_type": "act"}
                ],
                "description": "Mixed task types: act-edit-act pattern"
            }
        ]
    },
    "multitask-b": {
        "name": "Complex Multi-Task Scenarios",
        "tests": [
            {
                "id": "MT-B1",
                "name": "Four-task workflow",
                "text": "scroll to footer, click the newsletter signup, enter test@example.com, and submit the form",
                "expected_task_count": 4,
                "expected_tasks": [
                    {"contains": "scroll", "step_type": "act"},
                    {"contains": "click", "step_type": "act"},
                    {"contains": "enter", "step_type": "act"},
                    {"contains": "submit", "step_type": "act"}
                ],
                "description": "Complete user workflow with 4 actions"
            },
            {
                "id": "MT-B2",
                "name": "Design modifications sequence",
                "text": "make the header sticky, add a shadow to it, and change the logo size to 120px",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "sticky", "step_type": "edit"},
                    {"contains": "shadow", "step_type": "edit"},
                    {"contains": "120px", "step_type": "edit"}
                ],
                "description": "Multiple related design changes"
            },
            {
                "id": "MT-B3",
                "name": "Testing and validation flow",
                "text": "click the search icon, type 'react components', press enter, and verify results appear",
                "expected_task_count": 4,
                "expected_tasks": [
                    {"contains": "click", "step_type": "act"},
                    {"contains": "type", "step_type": "act"},
                    {"contains": "enter", "step_type": "act"},
                    {"contains": "verify", "step_type": "act"}
                ],
                "description": "Search workflow with verification"
            },
            {
                "id": "MT-B4",
                "name": "Single task that looks like multiple (false positive test)",
                "text": "add a button with text 'Save and Continue' to the form",
                "expected_task_count": 1,
                "expected_tasks": [
                    {"contains": "button", "step_type": "edit"}
                ],
                "description": "Should NOT split - 'and' is part of button text"
            },
            {
                "id": "MT-B5",
                "name": "Conjunctions in descriptions (false positive test)",
                "text": "create a navigation bar with links for Home, About, and Services",
                "expected_task_count": 1,
                "expected_tasks": [
                    {"contains": "navigation", "step_type": "edit"}
                ],
                "description": "List with 'and' - should be one task"
            }
        ]
    },
    "multitask-c": {
        "name": "Context Propagation & Queue Validation",
        "tests": [
            {
                "id": "MT-C1",
                "name": "Multi-task with context references",
                "text": "add a pricing card, make it blue, and add a button inside it",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "pricing card", "step_type": "edit"},
                    {"contains": "blue", "step_type": "edit"},
                    {"contains": "button", "step_type": "edit"}
                ],
                "validate_context_propagation": True,
                "description": "Each task should see previous tasks in context"
            },
            {
                "id": "MT-C2",
                "name": "First multi-task, then single task",
                "text": "scroll down and click the CTA button",
                "expected_task_count": 2,
                "expected_tasks": [
                    {"contains": "scroll", "step_type": "act"},
                    {"contains": "CTA", "step_type": "act"}
                ],
                "description": "Multi-task request followed by single"
            },
            {
                "id": "MT-C3",
                "name": "Single task after multi-task (context check)",
                "text": "change the button background to green",
                "expected_task_count": 1,
                "expected_tasks": [
                    {"contains": "green", "step_type": "edit"}
                ],
                "should_have_context": True,
                "description": "Should have context from previous multi-task"
            },
            {
                "id": "MT-C4",
                "name": "Another multi-task after mixed sequence",
                "text": "add padding to the button, center it, and make the text bold",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "padding", "step_type": "edit"},
                    {"contains": "center", "step_type": "edit"},
                    {"contains": "bold", "step_type": "edit"}
                ],
                "description": "Multi-task with context from previous requests"
            },
            {
                "id": "MT-C5",
                "name": "Long multi-task triggering summarization",
                "text": "scroll to the comprehensive dashboard section with detailed analytics, click on the performance metrics dropdown menu, and change the chart color scheme to use corporate brand colors",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "scroll", "step_type": "act"},
                    {"contains": "click", "step_type": "act"},
                    {"contains": "chart", "step_type": "edit"}
                ],
                "description": "Long multi-task that may trigger context summarization"
            }
        ]
    },
    "multitask-d": {
        "name": "Edge Cases & Stress Tests",
        "tests": [
            {
                "id": "MT-D1",
                "name": "Five-task complex workflow",
                "text": "open the modal, fill in the name field, fill in the email field, check the terms checkbox, and click submit",
                "expected_task_count": 5,
                "expected_tasks": [
                    {"contains": "modal", "step_type": "act"},
                    {"contains": "name", "step_type": "act"},
                    {"contains": "email", "step_type": "act"},
                    {"contains": "checkbox", "step_type": "act"},
                    {"contains": "submit", "step_type": "act"}
                ],
                "description": "Stress test: 5 sequential tasks - fill actions should be act"
            },
            {
                "id": "MT-D2",
                "name": "Semicolon-separated tasks",
                "text": "add a header; add a footer; style them both",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "header", "step_type": "edit"},
                    {"contains": "footer", "step_type": "edit"},
                    {"contains": "style", "step_type": "edit"}
                ],
                "description": "Alternative separator style with semicolons"
            },
            {
                "id": "MT-D3",
                "name": "Numbered list format",
                "text": "1. scroll to top 2. click the logo 3. verify homepage loads",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "scroll", "step_type": "act"},
                    {"contains": "logo", "step_type": "act"},
                    {"contains": "verify", "step_type": "act"}
                ],
                "description": "Tasks formatted as numbered list"
            },
            {
                "id": "MT-D4",
                "name": "Implicit sequence without conjunctions",
                "text": "add a contact form. make it centered. add submit button",
                "expected_task_count": 3,
                "expected_tasks": [
                    {"contains": "form", "step_type": "edit"},
                    {"contains": "centered", "step_type": "edit"},
                    {"contains": "button", "step_type": "edit"}
                ],
                "description": "Period-separated implicit sequence"
            },
            {
                "id": "MT-D5",
                "name": "Back-to-back multi-tasks (queue stress test)",
                "text": "hover over the dropdown and select the first option",
                "expected_task_count": 2,
                "expected_tasks": [
                    {"contains": "hover", "step_type": "act"},
                    {"contains": "select", "step_type": "act"}
                ],
                "description": "Quick succession for queue validation"
            }
        ]
    }
}


def get_all_multitask_tests():
    """Return all multi-task test cases with session IDs."""
    all_tests = []
    for session_id, session_data in MULTITASK_TEST_SESSIONS.items():
        for test in session_data["tests"]:
            test["session_id"] = session_id
            all_tests.append(test)
    return all_tests


def get_multitask_tests_by_session(session_id):
    """Return multi-task tests for a specific session."""
    if session_id in MULTITASK_TEST_SESSIONS:
        tests = MULTITASK_TEST_SESSIONS[session_id]["tests"]
        for test in tests:
            test["session_id"] = session_id
        return tests
    return []


def get_multitask_session_ids():
    """Return list of all multi-task session IDs."""
    return list(MULTITASK_TEST_SESSIONS.keys())

