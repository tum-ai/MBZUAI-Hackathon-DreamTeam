"""
Test definitions for editor agent.
Each test validates the two-step LLM process.
"""

EDITOR_TESTS = [
    # Decision Tests - Generate Actions
    {
        "id": "gen-button-1",
        "name": "Generate Button - Simple",
        "session_id": "test-gen-button-1",
        "step_id": "step-1",
        "intent": "Add a button that says Click Me",
        "context": "Building a landing page",
        "expected_action": "generate",
        "expected_component": "button",
        "expected_text": "Click Me"
    },
    {
        "id": "gen-text-1",
        "name": "Generate Text - Hero Title",
        "session_id": "test-gen-text-1",
        "step_id": "step-1",
        "intent": "Create a hero title that says Welcome to the Future",
        "context": "Building a hero section",
        "expected_action": "generate",
        "expected_component": "p",  # HTML text element (p, h1, h2, span, etc.)
        "expected_text": "Welcome to the Future"
    },
    {
        "id": "gen-box-1",
        "name": "Generate Box - Container",
        "session_id": "test-gen-box-1",
        "step_id": "step-1",
        "intent": "Create a flex container box for the hero section",
        "context": "Need a flex container with centered content",
        "expected_action": "generate",
        "expected_component": "div",
        "expected_style": {
            "display": None  # Should have display property for flex
        }
    },
    {
        "id": "gen-image-1",
        "name": "Generate Image - Hero Image",
        "session_id": "test-gen-image-1",
        "step_id": "step-1",
        "intent": "Add a hero background image",
        "context": "Building landing page",
        "expected_action": "generate",
        "expected_component": "img"
    },
    
    # Decision Tests - Edit Actions
    {
        "id": "edit-text-1",
        "name": "Edit Text - Increase Size",
        "session_id": "test-edit-text-1",
        "step_id": "step-1",
        "intent": "Make the hero title much larger, set font size to 72px",
        "context": "User wants to emphasize the title more",
        "expected_action": "edit",
        "expected_component": "p",  # HTML paragraph tag (or h1, h2, etc.)
        "expected_style": {
            "fontSize": None  # Should have fontSize property
        }
    },
    {
        "id": "edit-button-1",
        "name": "Edit Button - Change Color",
        "session_id": "test-edit-button-1",
        "step_id": "step-1",
        "intent": "Change the button background color to blue",
        "context": "Updating button styling",
        "expected_action": "edit",
        "expected_component": "button",
        "expected_style": {
            "backgroundColor": None  # Should have backgroundColor
        }
    },
    
    # Complex Generation Tests
    {
        "id": "gen-button-2",
        "name": "Generate Button - With Styling",
        "session_id": "test-gen-button-2",
        "step_id": "step-1",
        "intent": "Add a blue button that says Submit with rounded corners",
        "context": "Building a contact form",
        "expected_action": "generate",
        "expected_component": "button",
        "expected_text": "Submit",
        "expected_style": {
            "borderRadius": None  # Should have borderRadius
        }
    },
    {
        "id": "gen-text-2",
        "name": "Generate Text - Styled Heading",
        "session_id": "test-gen-text-2",
        "step_id": "step-1",
        "intent": "Create a large bold heading that says Get Started Today",
        "context": "Building CTA section",
        "expected_action": "generate",
        "expected_component": "p",  # HTML text element (h1, h2, p, etc.)
        "expected_text": "Get Started Today",
        "expected_style": {
            "fontSize": None,  # Should have fontSize
            "fontWeight": None  # Should have fontWeight for bold
        }
    },
    
    # Edge Cases
    {
        "id": "edge-1",
        "name": "Simple Navigation Link",
        "session_id": "test-edge-1",
        "step_id": "step-1",
        "intent": "Add a navigation link that says Home",
        "context": "Building website navigation",
        "expected_action": "generate",
        "expected_component": "a",  # Link component
        "expected_text": "Home"
    },
    {
        "id": "edge-2",
        "name": "Card with Gradient",
        "session_id": "test-edge-2",
        "step_id": "step-1",
        "intent": "Create a card with gradient background",
        "context": "Building features section",
        "expected_action": "generate",
        "expected_component": "div",  # Card or Box
        "expected_style": {
            "background": None  # Should have background with gradient
        }
    }
]


def get_all_tests():
    """Get all test cases."""
    return EDITOR_TESTS

