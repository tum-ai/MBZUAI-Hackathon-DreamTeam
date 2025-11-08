"""
Test case definitions for clarifier agent.
15 test cases covering diverse scenarios with ambiguous requests.
All tests run in parallel for efficiency.
"""

CLARIFIER_TESTS = [
    # Category 1: Ambiguous Pronouns
    {
        "id": "T01",
        "name": "Ambiguous pronoun - 'that' with multiple actions",
        "session_id": "clarifier-test-01",
        "step_id": "step-01-ambiguous-that",
        "intent": "Change that | User intends to modify a website element but refers to it as 'that', which is ambiguous. The previous context mentions scrolling to footer and clicking submit button.",
        "context": "Scroll down to the footer section | Click on the submit button",
        "description": "User says 'that' when referring to elements, context has multiple possibilities"
    },
    {
        "id": "T02",
        "name": "Ambiguous pronoun - 'it' with logo and text",
        "session_id": "clarifier-test-02",
        "step_id": "step-02-ambiguous-it",
        "intent": "Make it bigger | User wants to increase size but 'it' is ambiguous. Context includes adding a logo and changing header text.",
        "context": "Add logo image to header | Change header text to 'Welcome'",
        "description": "User says 'make it bigger' but unclear if referring to logo or text"
    },
    {
        "id": "T03",
        "name": "Ambiguous pronoun - 'this' with navigation and button",
        "session_id": "clarifier-test-03",
        "step_id": "step-03-ambiguous-this",
        "intent": "Fix this | User wants to fix something but 'this' could refer to the navigation menu or call-to-action button from previous context.",
        "context": "Create navigation menu with links | Add call-to-action button",
        "description": "User says 'fix this' after creating multiple elements"
    },
    
    # Category 2: Vague References
    {
        "id": "T04",
        "name": "Vague reference - 'thing on top'",
        "session_id": "clarifier-test-04",
        "step_id": "step-04-vague-top",
        "intent": "Update the thing on top | User refers to an element as 'the thing on top' which is vague. Context shows header with logo, navigation, and search bar.",
        "context": "Add header with logo | Create navigation bar | Add search functionality",
        "description": "Vague reference to 'thing on top' with multiple header elements"
    },
    {
        "id": "T05",
        "name": "Vague reference - 'stuff in middle'",
        "session_id": "clarifier-test-05",
        "step_id": "step-05-vague-middle",
        "intent": "Modify the stuff in the middle section | User wants to change 'the stuff in the middle section' which is unclear. Context includes hero section, features grid, and testimonials.",
        "context": "Create hero section with title | Add features grid with 6 items | Add testimonials section",
        "description": "Ambiguous reference to middle section content"
    },
    {
        "id": "T06",
        "name": "Vague reference - 'the element'",
        "session_id": "clarifier-test-06",
        "step_id": "step-06-vague-element",
        "intent": "Adjust the element | User says 'adjust the element' without specifying which one. Previous actions created form fields, labels, and submit button.",
        "context": "Add contact form with name and email fields | Add form labels | Style submit button",
        "description": "Generic reference to 'the element' with many form components"
    },
    
    # Category 3: Missing Information
    {
        "id": "T07",
        "name": "Missing info - color target",
        "session_id": "clarifier-test-07",
        "step_id": "step-07-missing-color-target",
        "intent": "Change the color | User wants to change a color but doesn't specify what element. Context shows card background, text, and border styling.",
        "context": "Create pricing card | Style card background | Add border to card",
        "description": "Color change request without specifying target element"
    },
    {
        "id": "T08",
        "name": "Missing info - resize target",
        "session_id": "clarifier-test-08",
        "step_id": "step-08-missing-resize",
        "intent": "Resize | User says 'resize' without specifying what or to what dimensions. Context includes image gallery with multiple images.",
        "context": "Add image gallery | Upload product images | Create image thumbnails",
        "description": "Resize request missing both target and dimensions"
    },
    {
        "id": "T09",
        "name": "Missing info - button position",
        "session_id": "clarifier-test-09",
        "step_id": "step-09-missing-position",
        "intent": "Add a button | User wants to add a button but doesn't specify where. Context shows existing footer, sidebar, and header.",
        "context": "Create footer with social links | Add sidebar navigation | Update header layout",
        "description": "Button addition without specifying location"
    },
    
    # Category 4: Edge Cases
    {
        "id": "T10",
        "name": "Conflicting context",
        "session_id": "clarifier-test-10",
        "step_id": "step-10-conflicting",
        "intent": "Change it back | User made contradictory changes and now wants to 'change it back' but unclear which change to revert. Context shows text color changed multiple times.",
        "context": "Change heading color to blue | Change heading color to red | Make heading bold",
        "description": "Conflicting previous actions make reference ambiguous"
    },
    {
        "id": "T11",
        "name": "Unclear scope - responsive",
        "session_id": "clarifier-test-11",
        "step_id": "step-11-unclear-scope",
        "intent": "Make it responsive | User wants responsive design but doesn't specify what component. Context includes layout, navigation, and images.",
        "context": "Create two-column layout | Add navigation menu | Add product images",
        "description": "Responsive request without specifying scope"
    },
    {
        "id": "T12",
        "name": "Special characters in request",
        "session_id": "clarifier-test-12",
        "step_id": "step-12-special-chars",
        "intent": "Update <that> & fix the 'other' one | User request contains special characters and vague references. Context shows modal dialog and tooltip.",
        "context": "Create modal dialog with close button | Add tooltip to info icon",
        "description": "Request with special characters and ambiguous references"
    },
    
    # Category 5: Complex & Unrelated
    {
        "id": "T13",
        "name": "Multiple ambiguities",
        "session_id": "clarifier-test-13",
        "step_id": "step-13-multiple",
        "intent": "Make that bigger and change its color to match the other one | User has multiple ambiguous references in single request. Context includes header, footer, and sidebar styling.",
        "context": "Style header with gradient background | Add footer with dark theme | Create sidebar with light colors",
        "description": "Multiple vague references in one request"
    },
    {
        "id": "T14",
        "name": "Technical jargon",
        "session_id": "clarifier-test-14",
        "step_id": "step-14-jargon",
        "intent": "Implement the WCAG AA compliance stuff | User uses technical jargon 'WCAG AA compliance stuff' which is vague. Context shows form and button creation.",
        "context": "Create login form | Add submit button | Style form inputs",
        "description": "Technical jargon requiring clarification on scope"
    },
    {
        "id": "T15",
        "name": "Unrelated/nonsensical query",
        "session_id": "clarifier-test-15",
        "step_id": "step-15-nonsensical",
        "intent": "The purple monkey dishwasher needs adjustment | Completely nonsensical request that doesn't relate to web development. Context shows normal website editing.",
        "context": "Create homepage layout | Add hero section with image",
        "description": "Completely unrelated and nonsensical user input"
    }
]


def get_all_tests():
    """Return all test cases."""
    return CLARIFIER_TESTS


def get_test_by_id(test_id):
    """Return a specific test case by ID."""
    for test in CLARIFIER_TESTS:
        if test["id"] == test_id:
            return test
    return None


def get_tests_by_category():
    """Return tests organized by category."""
    return {
        "ambiguous_pronouns": CLARIFIER_TESTS[0:3],
        "vague_references": CLARIFIER_TESTS[3:6],
        "missing_information": CLARIFIER_TESTS[6:9],
        "edge_cases": CLARIFIER_TESTS[9:12],
        "complex_unrelated": CLARIFIER_TESTS[12:15]
    }

