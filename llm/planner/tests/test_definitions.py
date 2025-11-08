"""
Test case definitions for planner agent.
30 test cases organized into 3 sessions for parallel execution.
"""

TEST_SESSIONS = {
    "session-a": {
        "name": "Core Functionality & Edge Cases",
        "tests": [
            {
                "id": "A1",
                "name": "Empty session - first prompt",
                "text": "Add a hero section with a title",
                "expected_intent": "edit",
                "expected_context_empty": True,
                "description": "First request with no previous context"
            },
            {
                "id": "A2",
                "name": "Second prompt - single context",
                "text": "Make the title bold and centered",
                "expected_intent": "edit",
                "expected_context_count": 1,
                "description": "Context should contain only 1 previous prompt"
            },
            {
                "id": "A3",
                "name": "Third prompt - full context window",
                "text": "Add a subtitle below the title",
                "expected_intent": "edit",
                "expected_context_count": 2,
                "description": "Context should contain last 2 prompts"
            },
            {
                "id": "A4",
                "name": "Short context - no summarization",
                "text": "Change color to blue",
                "expected_intent": "edit",
                "expected_context_short": True,
                "description": "Context <100 chars, should not trigger summarization"
            },
            {
                "id": "A5",
                "name": "Long context - triggers summarization",
                "text": "Add a navigation bar at the top with logo on the left, menu items in center, and call-to-action button on the right side",
                "expected_intent": "edit",
                "expected_context_long": True,
                "description": "Long prompt creates context >100 chars for next request"
            },
            {
                "id": "A6",
                "name": "Act intent - scroll action",
                "text": "Scroll down to the footer section",
                "expected_intent": "act",
                "description": "Should classify as action, not edit"
            },
            {
                "id": "A7",
                "name": "Act intent - click action",
                "text": "Click on the submit button",
                "expected_intent": "act",
                "description": "Click action should be classified as act"
            },
            {
                "id": "A8",
                "name": "Edit with context reference",
                "text": "Change that",
                "expected_intent": "edit",
                "acceptable_intents": ["edit", "clarify"],
                "description": "With context, 'that' refers to previous element"
            },
            {
                "id": "A9",
                "name": "Edit improvement request",
                "text": "Make it better",
                "expected_intent": "edit",
                "acceptable_intents": ["edit", "clarify"],
                "description": "Style improvement interpreted as edit"
            },
            {
                "id": "A10",
                "name": "Edit intent - style modification",
                "text": "Add padding and shadow to the card",
                "expected_intent": "edit",
                "description": "Clear style edit request"
            }
        ]
    },
    "session-b": {
        "name": "Intent Classification Accuracy",
        "tests": [
            {
                "id": "B1",
                "name": "Unambiguous edit - component creation",
                "text": "Create a pricing table with three columns showing basic, pro, and enterprise tiers",
                "expected_intent": "edit",
                "description": "Clear component creation request"
            },
            {
                "id": "B2",
                "name": "Unambiguous edit - layout change",
                "text": "Change the layout to a two-column grid",
                "expected_intent": "edit",
                "description": "Explicit layout modification"
            },
            {
                "id": "B3",
                "name": "Clear action - navigate",
                "text": "Navigate to the about page",
                "expected_intent": "act",
                "description": "Navigation action"
            },
            {
                "id": "B4",
                "name": "Clear action - hover",
                "text": "Hover over the menu icon",
                "expected_intent": "act",
                "description": "Hover interaction"
            },
            {
                "id": "B5",
                "name": "Vague reference with context",
                "text": "Fix the thing on top",
                "expected_intent": "clarify",
                "acceptable_intents": ["edit", "clarify"],
                "description": "Vague reference may be clear with context or need clarification"
            }
        ]
    },
    "session-c": {
        "name": "Stress Test & Variety",
        "tests": [
            {
                "id": "C1",
                "name": "Consecutive edit 1",
                "text": "Add a contact form with name, email, and message fields",
                "expected_intent": "edit",
                "description": "Start of consecutive edits"
            },
            {
                "id": "C2",
                "name": "Consecutive edit 2",
                "text": "Make the form fields have rounded corners",
                "expected_intent": "edit",
                "description": "Sequential edit builds on previous"
            },
            {
                "id": "C3",
                "name": "Consecutive edit 3",
                "text": "Add placeholder text to each field",
                "expected_intent": "edit",
                "description": "Third consecutive edit"
            },
            {
                "id": "C4",
                "name": "Mixed sequence - edit after act",
                "text": "Scroll to the testimonials section",
                "expected_intent": "act",
                "description": "Action after edits"
            },
            {
                "id": "C5",
                "name": "Edit after action",
                "text": "Change the testimonial card background to light gray",
                "expected_intent": "edit",
                "description": "Edit follows action"
            },
            {
                "id": "C6",
                "name": "Very short prompt with context",
                "text": "Red",
                "expected_intent": "edit",
                "acceptable_intents": ["edit", "clarify"],
                "description": "Single word with context means color change"
            },
            {
                "id": "C7",
                "name": "Very long prompt",
                "text": "Create a comprehensive dashboard with a sidebar navigation containing links to dashboard, analytics, reports, settings, and profile pages, a top header with search bar and notification bell, and a main content area displaying cards with key metrics including total users, revenue, conversion rate, and active sessions with appropriate icons and color coding for each metric",
                "expected_intent": "edit",
                "description": "Long complex edit request"
            },
            {
                "id": "C8",
                "name": "Special characters in prompt",
                "text": "Add a button with text 'Sign Up -> Free Trial!' and make it 50% width",
                "expected_intent": "edit",
                "description": "Prompt with special characters"
            },
            {
                "id": "C9",
                "name": "Numbers and units",
                "text": "Set the container max-width to 1200px and padding to 20px",
                "expected_intent": "edit",
                "description": "Technical specifications with units"
            },
            {
                "id": "C10",
                "name": "Multiple actions in sequence",
                "text": "Click the dropdown menu",
                "expected_intent": "act",
                "description": "Action request"
            },
            {
                "id": "C11",
                "name": "Context window boundary test 1",
                "text": "Add a footer with social media links",
                "expected_intent": "edit",
                "description": "Testing context sliding window"
            },
            {
                "id": "C12",
                "name": "Context window boundary test 2",
                "text": "Make the footer sticky at bottom",
                "expected_intent": "edit",
                "description": "Should only see last 2 prompts in context"
            },
            {
                "id": "C13",
                "name": "Step ID uniqueness check 1",
                "text": "Add a logo in the header",
                "expected_intent": "edit",
                "description": "For verifying unique step IDs"
            },
            {
                "id": "C14",
                "name": "Step ID uniqueness check 2",
                "text": "Make the logo 150px wide",
                "expected_intent": "edit",
                "description": "Another step ID to verify uniqueness"
            },
            {
                "id": "C15",
                "name": "Vague reference with context",
                "text": "Update the thing in the middle",
                "expected_intent": "clarify",
                "acceptable_intents": ["edit", "clarify"],
                "description": "Vague reference may be clear with context or need clarification"
            }
        ]
    }
}


def get_all_tests():
    """Return all test cases with session IDs."""
    all_tests = []
    for session_id, session_data in TEST_SESSIONS.items():
        for test in session_data["tests"]:
            test["session_id"] = session_id
            all_tests.append(test)
    return all_tests


def get_tests_by_session(session_id):
    """Return tests for a specific session."""
    if session_id in TEST_SESSIONS:
        tests = TEST_SESSIONS[session_id]["tests"]
        for test in tests:
            test["session_id"] = session_id
        return tests
    return []


def get_session_ids():
    """Return list of all session IDs."""
    return list(TEST_SESSIONS.keys())

