"""
Test case definitions for the actor agent.
Each test focuses on validating the actor pipeline without external dependencies.
"""

from copy import deepcopy


def _base_dom_snapshot():
    return {
        "snapshot": {
            "currentUrl": "/",
            "viewportHeight": 900,
            "scrollY": 0,
            "totalElementCount": 3,
            "iframeElementCount": 0,
            "elements": [
                {
                    "navId": "nav-home-link",
                    "tagName": "a",
                    "text": "Home",
                    "context": "main-app",
                    "isVisible": True,
                },
                {
                    "navId": "nav-about-link",
                    "tagName": "a",
                    "text": "About",
                    "context": "main-app",
                    "isVisible": True,
                },
                {
                    "navId": "hero-title",
                    "tagName": "h1",
                    "text": "Welcome",
                    "context": "main-app",
                    "isVisible": True,
                },
            ],
        },
        "timestamp": "2025-01-01T00:00:00.000Z",
    }


ACTOR_TESTS = [
    {
        "id": "actor-basic-navigate",
        "name": "Generate navigate action with DOM context",
        "session_id": "actor-session-001",
        "step_id": "step-001",
        "intent": "Take me to the about page",
        "context": "User wants more information about the company.",
        "mock_dom_snapshot_response": _base_dom_snapshot(),
        "mock_system_prompt": "SYSTEM PROMPT :: navigation",
        "mock_action_output": (
            '{"action":"navigate","targetId":"nav-about-link","reasoning":"User '
            'requested the about page."}'
        ),
        "expected_action_output": (
            '{"action":"navigate","targetId":"nav-about-link","reasoning":"User '
            'requested the about page."}'
        ),
        "seed_session": {"sid": "actor-session-001", "actions": {}},
    },
    {
        "id": "actor-snapshot-fallback",
        "name": "Graceful fallback when DOM snapshot fetch fails",
        "session_id": "actor-session-002",
        "step_id": "step-002",
        "intent": "Scroll down a bit",
        "context": "",
        "snapshot_error": RuntimeError("Websocket bridge unreachable"),
        "mock_system_prompt": "SYSTEM PROMPT :: empty snapshot",
        "mock_action_output": '{"action":"scroll","direction":"down","amount":500}',
        "expected_action_output": '{"action":"scroll","direction":"down","amount":500}',
        "seed_session": {"sid": "actor-session-002"},
    },
    {
        "id": "actor-session-merge",
        "name": "Appends action to existing session history",
        "session_id": "actor-session-003",
        "step_id": "step-003",
        "intent": "Focus the email input field",
        "context": "The user already entered their name.",
        "mock_dom_snapshot_response": {
            "snapshot": {
                "currentUrl": "/contact",
                "viewportHeight": 900,
                "scrollY": 120,
                "totalElementCount": 4,
                "iframeElementCount": 0,
                "elements": [
                    {
                        "navId": "name-input",
                        "tagName": "input",
                        "text": "",
                        "context": "main-app",
                        "isVisible": True,
                    },
                    {
                        "navId": "email-input",
                        "tagName": "input",
                        "text": "",
                        "context": "main-app",
                        "isVisible": True,
                    },
                    {
                        "navId": "submit-button",
                        "tagName": "button",
                        "text": "Submit",
                        "context": "main-app",
                        "isVisible": True,
                    },
                    {
                        "navId": "nav-contact-link",
                        "tagName": "a",
                        "text": "Contact",
                        "context": "main-app",
                        "isVisible": True,
                    },
                ],
            },
            "timestamp": "2025-01-01T00:05:00.000Z",
        },
        "mock_system_prompt": "SYSTEM PROMPT :: forms",
        "mock_action_output": '{"action":"focus","targetId":"email-input"}',
        "expected_action_output": '{"action":"focus","targetId":"email-input"}',
        "seed_session": {
            "sid": "actor-session-003",
            "actions": {
                "step-previous": {
                    "intent": "Type the user name",
                    "context": "Collecting contact details",
                    "action": '{"action":"type","targetId":"name-input","text":"John"}',
                }
            },
        },
        "expected_existing_action_ids": ["step-previous"],
    },
]


def get_all_tests():
    """Return all actor test cases."""
    return ACTOR_TESTS


def get_test_by_id(test_id: str):
    """Retrieve a specific test case by ID."""
    for test in ACTOR_TESTS:
        if test["id"] == test_id:
            return deepcopy(test)
    return None

