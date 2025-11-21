from pathlib import Path
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import httpx

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

MODEL_NAME = "MBZUAI-IFM/K2-Think"
BASE_URL = "https://llm-api.k2think.ai/v1"

_K2_CLIENT = None


def get_k2_client():
    """Get or create cached K2 Think OpenAI client."""
    global _K2_CLIENT
    if _K2_CLIENT is None:
        api_key = os.getenv("K2_API_KEY")
        if not api_key:
            raise ValueError("K2_API_KEY not found in environment variables")
        
        http_client = httpx.Client(
            timeout=1200.0,
            follow_redirects=True
        )
        
        _K2_CLIENT = OpenAI(
            base_url=BASE_URL,
            api_key=api_key,
            timeout=1200.0,
            max_retries=2,
            http_client=http_client
        )
    
    return _K2_CLIENT


def generate_component_direct(intent: str, context: str, manifests: dict, current_ast: dict = None) -> dict:
    """
    Generate a component directly in a single LLM call.
    Combines decision and generation into one step for optimal performance.
    
    Args:
        intent: User's request with explanation
        context: Previous actions/prompts for context
        manifests: Dictionary of available component manifests
        current_ast: Current page AST (optional, for edit actions)
    
    Returns:
        Component JSON object
    """
    client = get_k2_client()
    
    # Include AST context if provided (for editing existing components)
    ast_section = ""
    if current_ast:
        ast_str = json.dumps(current_ast, indent=2)
        ast_section = f"""

**CURRENT_PAGE_AST**:
```json
{ast_str}
```"""
    
    # Structured prompt inspired by compiler's prompt.md
    prompt = f"""**USER REQUEST**: {intent}

**CONTEXT**: {context}{ast_section}

**AVAILABLE COMPONENTS**:
- Box (div): layout container. Props: style, as ("div"|"section"|"header"|"footer"). Slots: ["default"]
- Text (p): all text. Props: content, style, as ("p"|"h1"|"h2"|"h3"|"span"). Slots: {{}}
- Button: interactive button. Props: text, style. Slots: ["default"]. Events: ["click"]
- Image: img. Props: src, alt, style. Slots: {{}}
- Link (a): hyperlink. Props: href, target, style. Slots: ["default"]
- List (ul): list. Props: items (array), style. Slots: ["default"]
- Table: table. Props: headers (array), rows (array[array]), style. Slots: {{}}
- Textbox (input): input field. Props: placeholder, modelValue (state binding), style. Events: ["input"]
- Icon (svg): icon. Props: svgPath, viewBox, style. Slots: {{}}
- Card: styled container. Props: style, variant ("default"|"elevated"|"outlined"). Slots: ["default","header","footer"]
- GradientText: animated gradient text. Props: content, as, gradientFrom, gradientTo, animated. Slots: {{}}
- Accordion: collapsible section. Props: title, isOpen (state), icon. Slots: ["default"]. Events: ["click"]

**RULES**:
- Output ONLY JSON (no markdown, no text)
- id: semantic kebab-case (e.g., "submit-button", "hero-title", "feature-card")
- type: exact component name from list above
- props: style object with camelCase keys (fontSize, backgroundColor, padding, margin, etc.)
- slots: {{}} or {{"default": [child components]}}
- Modern professional styling: flexbox/grid, good spacing, clean colors

**EXAMPLE**:
{{
  "id": "submit-button",
  "type": "Button",
  "props": {{
    "text": "Submit",
    "style": {{
      "fontSize": "16px",
      "padding": "10px 20px",
      "backgroundColor": "#007bff",
      "color": "#fff",
      "border": "none",
      "borderRadius": "4px"
    }}
  }},
  "slots": {{}}
}}"""

    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse response handling <think> and <answer> tags
    try:
        if "<answer>" in content and "</answer>" in content:
            content = content.split("<answer>")[1].split("</answer>")[0].strip()
        elif "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        component = json.loads(content)
        
        # Validate required fields
        if "id" not in component:
            component["id"] = "generated-component"
        if "type" not in component:
            component["type"] = "Box"
        
        return component
    except (json.JSONDecodeError, ValueError) as e:
        # Return minimal valid component
        return {
            "id": "error-component",
            "type": "Box",
            "props": {},
            "slots": {},
            "error": f"Could not parse component: {str(e)}"
        }


# (not used in optimized path)
def decide_component_action(intent: str, context: str, manifests: dict) -> dict:
    """
    Step 1: Decide whether to generate or edit, and which component type.
    
    Args:
        intent: User's request with explanation
        context: Previous actions/prompts for context
        manifests: Dictionary of available component manifests
    
    Returns:
        {"action": "generate" | "edit", "component_type": "Button" | "Text" | ...}
    """
    client = get_k2_client()
    
    manifest_list = []
    for name, manifest in manifests.items():
        manifest_list.append(f"- {name}: {manifest.get('componentName', name)}")
    manifests_str = "\n".join(manifest_list)
    
    prompt = f"""You are an expert AI component analyzer. Analyze the user's request and decide two things:

1. **ACTION**: Should we generate a new component or edit an existing one?
   - "generate": User wants to add/create something new
   - "edit": User wants to modify/change something that already exists

2. **COMPONENT_TYPE**: Which component type best matches the user's intent?

**USER_REQUEST**: {intent}

**CONTEXT**: {context}

**AVAILABLE COMPONENTS**:
{manifests_str}

**YOUR TASK**:
Analyze the request and respond with ONLY a JSON object in this exact format:
{{
  "action": "generate" or "edit",
  "component_type": "exact component name from the list above"
}}

**RULES**:
- If the user says "add", "create", "make a new", "insert" → action is "generate"
- If the user says "change", "modify", "update", "make it", "edit" → action is "edit"
- Choose the component_type that best matches the user's intent (Button for buttons, Text for text/titles, Box for containers, etc.)
- Component_type MUST be one of the available components listed above
- Output ONLY the JSON object, no other text

Examples:
- "Add a button that says Click Me" → {{"action": "generate", "component_type": "Button"}}
- "Make the title larger" → {{"action": "edit", "component_type": "Text"}}
- "Create a hero section" → {{"action": "generate", "component_type": "Box"}}
- "Change the button color to blue" → {{"action": "edit", "component_type": "Button"}}"""

    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse response handling <think> and <answer> tags
    try:
        if "<answer>" in content and "</answer>" in content:
            content = content.split("<answer>")[1].split("</answer>")[0].strip()
        elif "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Validate required fields
        if "action" not in result or "component_type" not in result:
            raise ValueError("Missing required fields in response")
        
        return result
    except (json.JSONDecodeError, ValueError) as e:
        # Fallback
        return {
            "action": "generate",
            "component_type": "Box",
            "error": f"Could not parse decision: {str(e)}"
        }


def generate_or_edit_component(intent: str, context: str, action: str, component_manifest: dict, current_ast: dict = None) -> dict:
    """
    Step 2: Generate or edit the component based on the decision.
    
    Args:
        intent: User's request with explanation
        context: Previous actions/prompts for context
        action: "generate" or "edit"
        component_manifest: The specific component manifest to use
        current_ast: Current page AST (required if action is "edit")
    
    Returns:
        Component JSON object
    """
    client = get_k2_client()
    
    component_name = component_manifest.get("friendlyName", component_manifest.get("componentName", "Component"))
    manifest_str = json.dumps(component_manifest, indent=2)
    
    if action == "edit":
        ast_str = json.dumps(current_ast, indent=2) if current_ast else "{}"
        prompt = f"""You are an expert AI component editor. Edit an existing {component_name} component based on the user's request.

**USER_REQUEST**: {intent}

**CONTEXT**: {context}

**COMPONENT MANIFEST** ({component_name}):
```json
{manifest_str}
```

**CURRENT PAGE AST**:
```json
{ast_str}
```

**YOUR TASK**:
Find the {component_name} component in the AST that the user wants to edit and generate the COMPLETE modified component JSON.

**RULES**:
- Output ONLY a valid JSON object for the component
- Include all required fields: id, type, props, slots
- The "type" field must match the componentName from the manifest
- Generate a human-readable id (e.g., "hero-title", "submit-button")
- All style properties must be camelCase (fontSize, backgroundColor, etc.)
- If modifying styles, merge with existing styles
- Preserve slots structure from the manifest

**OUTPUT FORMAT**:
{{
  "id": "component-id",
  "type": "{component_manifest.get('componentName', component_name)}",
  "props": {{
    "style": {{}},
    ...other props from manifest
  }},
  "slots": {{}}
}}

Output ONLY the JSON object, no other text."""
    else:  # action == "generate"
        prompt = f"""You are an expert AI component generator. Create a new {component_name} component based on the user's request.

**USER_REQUEST**: {intent}

**CONTEXT**: {context}

**COMPONENT MANIFEST** ({component_name}):
```json
{manifest_str}
```

**YOUR TASK**:
Generate a complete component JSON object that fulfills the user's request.

**RULES**:
- Output ONLY a valid JSON object for the component
- Include all required fields: id, type, props, slots
- The "type" field must be: "{component_manifest.get('componentName', component_name)}"
- Generate a unique, human-readable id (e.g., "hero-title", "submit-button", "contact-form")
- All style properties must be camelCase (fontSize, backgroundColor, padding, margin, etc.)
- Use professional, modern styling (think Apple, DeepMind websites)
- For layouts: use display: "flex" or "grid"
- For spacing: use padding and margin (e.g., "2rem", "20px")
- For colors: use hex codes or modern color names
- Preserve slots structure from the manifest

**STYLE GUIDELINES**:
- Make it look modern and professional
- Use proper spacing (padding: "1rem 2rem")
- Use readable fonts (fontSize: "16px" or "1.5rem")
- Use appropriate colors for context

**OUTPUT FORMAT**:
{{
  "id": "unique-component-id",
  "type": "{component_manifest.get('componentName', component_name)}",
  "props": {{
    "style": {{
      "fontSize": "16px",
      "padding": "10px 20px"
    }},
    ...other props based on manifest
  }},
  "slots": {{}}
}}

Output ONLY the JSON object, no other text."""

    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse response handling <think> and <answer> tags
    try:
        if "<answer>" in content and "</answer>" in content:
            content = content.split("<answer>")[1].split("</answer>")[0].strip()
        elif "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        component = json.loads(content)
        
        if "id" not in component:
            component["id"] = "generated-component"
        if "type" not in component:
            component["type"] = component_manifest.get("componentName", component_name)
        
        return component
    except (json.JSONDecodeError, ValueError) as e:
        # return minimal valid component
        return {
            "id": "error-component",
            "type": component_manifest.get("componentName", component_name),
            "props": {},
            "slots": {},
            "error": f"Could not parse component: {str(e)}"
        }


def generate_vue_component_direct(intent: str, existing_content: str) -> str:
    """
    Generate a complete Vue Single File Component (SFC) based on the user's intent and existing content.
    
    Args:
        intent: User's request
        existing_content: Current content of the Vue file
    
    Returns:
        Complete Vue SFC code (template, script, style)
    """
    client = get_k2_client()
    
    prompt = f"""You are an expert Vue.js developer. Your task is to UPDATE an existing Vue Single File Component (SFC) based on the user's request.

**USER REQUEST**: {intent}

**EXISTING FILE CONTENT**:
```vue
{existing_content}
```

**INSTRUCTIONS**:
1.  Analyze the existing content and the user's request.
2.  Output the **COMPLETE, UPDATED** Vue SFC code.
3.  Include `<script setup>`, `<template>`, and `<style scoped>` tags.
4.  **DO NOT** output markdown code fences (like ```vue ... ```). Output **ONLY** the raw code.
5.  Ensure the code is valid Vue 3 using the Composition API (`<script setup>`).
6.  Preserve existing functionality unless the user explicitly asks to change it.
7.  If the user asks to add a component or feature, implement it fully using standard HTML/CSS or existing components if inferred.
8.  Make the design modern and professional (Apple/DeepMind style) if adding new UI elements.

**OUTPUT**:
"""

    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    
    content = response.choices[0].message.content.strip()
    
    # Clean up markdown code blocks if present
    if content.startswith("```vue"):
        content = content[6:]
    elif content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
        
    if content.endswith("```"):
        content = content[:-3]
        
    # Strip <think> tags and content
    import re
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # Strip <answer> tags (keep content inside)
    content = content.replace("<answer>", "").replace("</answer>", "")
    
    # Strip any leading text before the first <template> or <script>
    # This helps if the model outputs "Here is the code:" before the actual code
    match = re.search(r'(<template>|<script)', content)
    if match:
        content = content[match.start():]
        
    return content.strip()
