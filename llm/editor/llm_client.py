from pathlib import Path
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import httpx

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

MODEL_NAME = "MBZUAI-IFM/K2-Think"
BASE_URL = "https://llm-api.k2think.ai/v1"


def get_k2_client():
    """Initialize and return K2 Think OpenAI client."""
    api_key = os.getenv("K2_API_KEY")
    if not api_key:
        raise ValueError("K2_API_KEY not found in environment variables")
    
    http_client = httpx.Client(
        timeout=1200.0,
        follow_redirects=True
    )
    
    return OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
        timeout=1200.0,
        max_retries=2,
        http_client=http_client
    )


def generate_json_patch(intent: str, context: str, manifests: dict, current_ast: dict, project_config: dict) -> list:
    """
    Generate JSON Patch array based on user intent and current AST.
    
    Args:
        intent: User's request with explanation
        context: Previous actions/prompts for context
        manifests: Dictionary of available component manifests
        current_ast: Current page AST (from home.json)
        project_config: Project configuration (from project.json)
    
    Returns:
        List of JSON Patch operations (RFC 6902 format)
    """
    client = get_k2_client()
    
    manifests_str = json.dumps(manifests, indent=2)
    current_ast_str = json.dumps(current_ast, indent=2)
    project_config_str = json.dumps(project_config, indent=2)
    
    prompt = f"""# **🤖 ROLE: AI AST COMPILER**

You are an expert AI Web Developer and systems architect. Your **sole purpose** is to act as a "compiler" that translates a user's natural language request into a precise **JSON Patch (RFC 6902) array**.

You will be given the user's request and the current state of the project (as JSON). You will analyze the user's intent and the current state, and you will generate *only* the JSON Patch array required to achieve the user's goal.

# **📝 INPUT FORMAT**

You have received:

1. **USER_REQUEST**: {intent}

2. **PROJECT_CONFIG**:
```json
{project_config_str}
```

3. **CURRENT_PAGE_AST**:
```json
{current_ast_str}
```

4. **CONTEXT**: {context}

# **🎯 OUTPUT FORMAT**

You **MUST** respond with **ONLY** a single, valid, parsable JSON array of patch operations.

* **DO NOT** include any other text, markdown (```json ...), or explanations outside the JSON array.
* Your entire response must be a single JSON block.

# **🧠 MANDATORY THOUGHT PROCESS**

Before generating the final JSON, you **MUST** engage in a step-by-step "thought" process. This is for your own planning.

**Thought Process:**

1. **Analyze Intent:** What *exactly* does the user want to do? (e.g., "Add a new component," "Change a style," "Add a new page," "Create a state variable").
2. **Identify Target(s):**
   * Am I modifying the whole project or just one page?
   * If "make the site dark" or "add a font," my target is PROJECT_CONFIG and the path is /globalStyles.
   * If "add a title," my target is CURRENT_PAGE_AST and the path is likely /tree/slots/default/- (to add) or /tree/slots/default/0 (to modify).
   * If "add a new page," my target is PROJECT_CONFIG and the path is /pages/-.
3. **Formulate Patches:** What op (add, replace, remove) is needed? What is the value?
   * Do I need to create a new component? If so, I will construct its full JSON object based on the Component Schema.
   * Do I need to add state? If so, I will add to the /state/myNewVariable path in CURRENT_PAGE_AST.
   * Do I need to add interactivity? If so, I will add an events block using the Action Schema.
4. **Style & Design (CRITICAL):** How do I make this look like a professional, modern website (e.g., Apple, DeepMind)?
   * **Layout:** I will use display: "grid" or display: "flex" on a Box for all layouts.
   * **Centering:** I will use alignItems: "center" and justifyContent: "center".
   * **Overlays:** I will use position: "relative" on a parent Box, and position: "absolute" on child components (like Image and a gradient Box). I will use z-index to layer them.
   * **Gradients:** I will create a Box with background: "linear-gradient(to top, #000, transparent)" to make text visible over images.
   * **Full Screen:** I will use height: "100vh" for hero sections.
   * **Spacing:** I will use padding and margin (e.g., padding: "2rem").
   * **Fonts/Colors:** I will define global styles in PROJECT_CONFIG's /globalStyles or add inline style props.
   * **Images:** When adding a placeholder image, I will prefer a dynamic, high-quality one like https://picsum.photos/1920/1080 to make the design look professional.
5. **Review Patches:** Is the JSON valid? Does it respect the component manifests? Is the path correct?

# **📚 AVAILABLE COMPONENTS**

Here are the component manifests you can use:

```json
{manifests_str}
```

# **📝 CORE RULES**

* **Output ONLY JSON.** No pleasantries.
* **Strings must be raw:** All string values must be raw text. Do not use HTML entities (e.g., use & not &amp;, use ' not &apos;).
* All style keys MUST be camelCase (e.g., backgroundColor, fontSize, zIndex). The generator handles conversion.
* All component types MUST match a friendlyName from the Component Manifests (e.g., "Box", "Text", "Button").
* All events MUST use an actionType from the Action Schema.
* **ALWAYS** generate a unique, human-readable id for all new components (e.g., hero-section, hero-title).
* To add multiple changes (e.g., add state *and* add a component), create a **single array with multiple patch operations**.

# **📚 ACTION SCHEMA**

* **action:setState**: {{"type": "action:setState", "stateKey": "myVar", "newValue": "new-value"}}
* **action:showAlert**: {{"type": "action:showAlert", "message": "Form submitted!"}}
* **action:scrollTo**: {{"type": "action:scrollTo", "target": "#my-section-id"}}

# **📚 STATE & EXPRESSIONS**

* **State:** Add state variables to CURRENT_PAGE_AST at /state/myVar.
  * `{{"op": "add", "path": "/state/myVar", "value": {{"type": "string", "defaultValue": "Hello"}}}}`
* **Expressions:** To bind state, use an expression object.
  * **Text Content:** `props: {{"content": {{"type": "expression", "value": "Thanks, ${{state.contactName}}!"}}}}`
  * **Event Logic:** `newValue: {{"type": "expression", "value": "(${{state.currentSlide}} + 1) % 3"}}`
  * **Input Binding:** `props: {{"modelValue": {{"type": "stateBinding", "stateKey": "contactName"}}}}`

# **📚 CONDITIONAL RENDERING**

To show/hide components (like popups or carousels), add a top-level v-if property to any component:

* **By State Key:** `{{ ... , "v-if": {{"stateKey": "isMenuOpen"}}}}`
* **By Expression:** `{{ ... , "v-if": {{"expression": "currentSlide === 0"}}}}` (State vars are used *without* ${{state.}} here).

Now, based on the user's request and the current state, generate the JSON Patch array."""

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
        
        # Parse and validate it's a valid JSON array
        patch_array = json.loads(content)
        
        if not isinstance(patch_array, list):
            raise ValueError("Response is not a JSON array")
        
        return patch_array
    except (json.JSONDecodeError, IndexError, ValueError) as e:
        # Return a fallback error patch
        return [{
            "error": f"Could not parse JSON Patch. Original response: {content[:200]}...",
            "exception": str(e)
        }]

