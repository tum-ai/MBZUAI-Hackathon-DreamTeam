"""
Test definitions for orchestration pipeline.
Tests the full workflow via /plan endpoint covering EDIT, ACT, CLARIFY, and mixed scenarios.
"""

ORCHESTRATION_TESTS = [
    # =================================================================
    # SINGLE-AGENT WORKFLOWS - EDIT Only
    # =================================================================
    {
        "id": "orch-edit-01",
        "name": "Single EDIT - Create button",
        "sid": "orch-edit-01",
        "text": "Create a blue button that says Submit",
        "description": "Simple single-task EDIT workflow",
        "expected_tasks": 1,
        "expected_agents": ["edit"]
    },
    {
        "id": "orch-edit-02",
        "name": "Single EDIT - Style modification",
        "sid": "orch-edit-02",
        "text": "Make the heading larger and bold",
        "description": "Simple style modification EDIT",
        "expected_tasks": 1,
        "expected_agents": ["edit"]
    },
    {
        "id": "orch-edit-03",
        "name": "Single EDIT - Complex component",
        "sid": "orch-edit-03",
        "text": "Add a navigation bar with logo on left and menu items on right",
        "description": "Complex single-task EDIT",
        "expected_tasks": 1,
        "expected_agents": ["edit"]
    },
    
    # =================================================================
    # SINGLE-AGENT WORKFLOWS - ACT Only
    # =================================================================
    {
        "id": "orch-act-01",
        "name": "Single ACT - Click action",
        "sid": "orch-act-01",
        "text": "Click the submit button",
        "description": "Simple single-task ACT workflow",
        "expected_tasks": 1,
        "expected_agents": ["act"]
    },
    {
        "id": "orch-act-02",
        "name": "Single ACT - Scroll action",
        "sid": "orch-act-02",
        "text": "Scroll down to the footer",
        "description": "Scroll action ACT workflow",
        "expected_tasks": 1,
        "expected_agents": ["act"]
    },
    {
        "id": "orch-act-03",
        "name": "Single ACT - Navigation",
        "sid": "orch-act-03",
        "text": "Navigate to the about page",
        "description": "Navigation ACT workflow",
        "expected_tasks": 1,
        "expected_agents": ["act"]
    },
    
    # =================================================================
    # SINGLE-AGENT WORKFLOWS - CLARIFY Only
    # =================================================================
    {
        "id": "orch-clarify-01",
        "name": "Single CLARIFY - Ambiguous reference",
        "sid": "orch-clarify-01",
        "text": "Change the thing at the top",
        "description": "Ambiguous request requiring clarification",
        "expected_tasks": 1,
        "expected_agents": ["clarify"]
    },
    {
        "id": "orch-clarify-02",
        "name": "Single CLARIFY - Vague instruction",
        "sid": "orch-clarify-02",
        "text": "Make it better",
        "description": "Vague request needing clarification",
        "expected_tasks": 1,
        "expected_agents": ["clarify"]
    },
    
    # =================================================================
    # MULTI-TASK WORKFLOWS - Same Agent Type
    # =================================================================
    {
        "id": "orch-multi-edit-01",
        "name": "Multi EDIT - Two edits",
        "sid": "orch-multi-edit-01",
        "text": "Create a login form and make the submit button blue",
        "description": "Two EDIT tasks in sequence",
        "expected_tasks": 2,
        "expected_agents": ["edit", "edit"]
    },
    {
        "id": "orch-multi-edit-02",
        "name": "Multi EDIT - Three edits",
        "sid": "orch-multi-edit-02",
        "text": "Add a hero section with title, then add a subtitle below it, and make both centered",
        "description": "Three EDIT tasks in sequence",
        "expected_tasks": 3,
        "expected_agents": ["edit", "edit", "edit"]
    },
    {
        "id": "orch-multi-act-01",
        "name": "Multi ACT - Two actions",
        "sid": "orch-multi-act-01",
        "text": "Scroll down and then click the contact button",
        "description": "Two ACT tasks in sequence",
        "expected_tasks": 2,
        "expected_agents": ["act", "act"]
    },
    
    # =================================================================
    # MULTI-TASK WORKFLOWS - Mixed Agents
    # =================================================================
    {
        "id": "orch-mixed-01",
        "name": "Mixed - EDIT then ACT",
        "sid": "orch-mixed-01",
        "text": "Create a submit button and then click it",
        "description": "EDIT followed by ACT",
        "expected_tasks": 2,
        "expected_agents": ["edit", "act"]
    },
    {
        "id": "orch-mixed-02",
        "name": "Mixed - ACT then EDIT",
        "sid": "orch-mixed-02",
        "text": "Scroll to footer and change its background to dark gray",
        "description": "ACT followed by EDIT",
        "expected_tasks": 2,
        "expected_agents": ["act", "edit"]
    },
    {
        "id": "orch-mixed-03",
        "name": "Mixed - EDIT, ACT, EDIT sequence",
        "sid": "orch-mixed-03",
        "text": "Add a pricing table, scroll to it, and then update the prices",
        "description": "Complex mixed workflow",
        "expected_tasks": 3,
        "expected_agents": ["edit", "act", "edit"]
    },
    {
        "id": "orch-mixed-04",
        "name": "Mixed - All agent types",
        "sid": "orch-mixed-04",
        "text": "Create a form, click the first field, and adjust something about the layout",
        "description": "EDIT, ACT, and potentially CLARIFY",
        "expected_tasks": 3,
        "expected_agents": ["edit", "act", "edit"]  # "adjust something" might be edit or clarify
    },
    
    # =================================================================
    # EDGE CASES
    # =================================================================
    {
        "id": "orch-edge-01",
        "name": "Edge - Very short request",
        "sid": "orch-edge-01",
        "text": "Blue button",
        "description": "Minimal request with limited context",
        "expected_tasks": 1,
        "expected_agents": ["edit"]
    },
    {
        "id": "orch-edge-02",
        "name": "Edge - Very long complex request",
        "sid": "orch-edge-02",
        "text": "Create a comprehensive dashboard with sidebar navigation containing links to dashboard, analytics, reports, and settings, then add a top header with search bar and notifications, and finally add metric cards showing user count, revenue, and conversion rates",
        "description": "Long complex multi-task request",
        "expected_tasks": 3,
        "expected_agents": ["edit", "edit", "edit"]
    },
    {
        "id": "orch-edge-03",
        "name": "Edge - Special characters",
        "sid": "orch-edge-03",
        "text": "Add a button with text 'Sign Up -> Start Free!' and make it 100% width",
        "description": "Request with special characters",
        "expected_tasks": 2,
        "expected_agents": ["edit", "edit"]
    },
    {
        "id": "orch-edge-04",
        "name": "Edge - Technical specifications",
        "sid": "orch-edge-04",
        "text": "Set container max-width to 1200px, padding to 20px, and margin to auto",
        "description": "Technical CSS specifications",
        "expected_tasks": 1,
        "expected_agents": ["edit"]
    },
    {
        "id": "orch-edge-05",
        "name": "Edge - Sequential actions with context",
        "sid": "orch-edge-05",
        "text": "Add a card with pricing info, make it have rounded corners, and add a shadow effect",
        "description": "Multiple related edits building on each other",
        "expected_tasks": 3,
        "expected_agents": ["edit", "edit", "edit"]
    }
]


def get_all_tests():
    """Get all test cases."""
    return ORCHESTRATION_TESTS


def get_tests_by_category(category):
    """
    Get tests by category.
    Categories: 'edit', 'act', 'clarify', 'multi-edit', 'multi-act', 'mixed', 'edge'
    """
    filtered = []
    for test in ORCHESTRATION_TESTS:
        if category in test["id"]:
            filtered.append(test)
    return filtered


def get_test_by_id(test_id):
    """Get a specific test by ID."""
    for test in ORCHESTRATION_TESTS:
        if test["id"] == test_id:
            return test
    return None

