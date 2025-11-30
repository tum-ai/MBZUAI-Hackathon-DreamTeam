"""
Editor Agent - Generates Vue SFC files for pages and components.
Updated to generate complete .vue files instead of JSON.
"""
import os
import re
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pathlib import Path

logger = logging.getLogger(__name__)

# Load editor prompt
PROMPTS_DIR = Path(__file__).parent / "prompts"
EDITOR_PROMPT_FILE = PROMPTS_DIR / "editor_prompt.md"

def load_editor_prompt():
    """Load the editor system prompt from file"""
    if EDITOR_PROMPT_FILE.exists():
        with open(EDITOR_PROMPT_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

EDITOR_SYSTEM_PROMPT = load_editor_prompt()


async def generate_vue_page(
    page_name: str,
    intent: str,
    context: str = "",
    existing_pages: list = None
) -> str:
    """
    Generate a complete Vue SFC page file.
    
    Args:
        page_name: Name of the page (e.g., "Home", "About")
        intent: What the user wants (e.g., "Create an about page with team info")
        context: Additional context
        existing_pages: List of existing page names
        
    Returns:
        Complete Vue SFC code as string
    """
    logger.info(f"[EDITOR] Generating Vue page: {page_name}")
    
    existing_pages_str = ", ".join(existing_pages) if existing_pages else "None"
    
    prompt = f"""Generate a complete Vue 3 Single File Component for a **{page_name}** page.

**User Request**: {intent}
**Context**: {context}
**Existing Pages**: {existing_pages_str}

**Requirements**:
1. Use Vue 3 Composition API with <script setup>
2. Use TailwindCSS for ALL styling (no custom CSS needed)
3. Include a sticky navigation bar with links to all pages
4. Make it fully responsive (mobile-first)
5. Use modern, clean design with dark theme
6. Include a footer at the bottom

**Navigation Bar Template**:
```html
<nav class="sticky top-0 bg-black/70 backdrop-blur-lg z-50 border-b border-gray-800">
  <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
    <h3 class="text-xl font-bold">My Website</h3>
    <div class="flex gap-6">
      <router-link to="/" class="text-gray-400 hover:text-white transition">Home</router-link>
      <!-- Add more nav links here -->
    </div>
    <button class="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-full transition">
      Get Started
    </button>
  </div>
</nav>
```

**Footer Template**:
```html
<footer class="border-t border-gray-800 py-8 text-center text-gray-500">
  <p>© 2025 My Website. All rights reserved.</p>
</footer>
```

**Output Format**:
Return ONLY the complete .vue file code. No explanations, no markdown code fences, just the raw Vue SFC.

Example structure:
<script setup>
// Any reactive state or imports
</script>

<template>
  <div class="min-h-screen bg-black text-white">
    <!-- Navigation -->
    <!-- Page content -->
    <!-- Footer -->
  </div>
</template>

<style scoped>
/* Optional scoped styles */
</style>

Generate the complete {page_name} page now:
"""
    
    # Initialize LLM
    k2_llm_uri = os.getenv("K2_LLM_URI", "http://localhost:11434/v1")
    k2_llm_api_key = os.getenv("K2_LLM_API_KEY", "dummy-key")
    
    llm = ChatOpenAI(
        base_url=k2_llm_uri,
        api_key=k2_llm_api_key,
        model="MBZUAI-IFM/K2-Think",
        temperature=0.7,
    )
    
    logger.info(f"[EDITOR] Invoking LLM for page generation...")
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        raw_content = response.content
        
        logger.info(f"[EDITOR] Received LLM response, length: {len(raw_content)}")
        
        # Clean the response
        vue_code = clean_vue_response(raw_content)
        
        logger.info(f"[EDITOR] Successfully generated {page_name} page")
        return vue_code
        
    except Exception as e:
        logger.error(f"[EDITOR] Error generating page: {e}")
        raise


async def generate_vue_component(
    component_name: str,
    intent: str,
    context: str = ""
) -> str:
    """
    Generate a reusable Vue component.
    
    Args:
        component_name: Name of component (e.g., "Button", "Card")
        intent: What the user wants
        context: Additional context
        
    Returns:
        Complete Vue SFC code
    """
    logger.info(f"[EDITOR] Generating Vue component: {component_name}")
    
    prompt = f"""Generate a reusable Vue 3 component: **{component_name}**

**User Request**: {intent}
**Context**: {context}

**Requirements**:
1. Use <script setup> with props/emits as needed
2. Use TailwindCSS for styling
3. Make it reusable and composable
4. Include proper TypeScript-style prop definitions

**Output**: Return ONLY the .vue file code, no explanations.

Example:
<script setup>
defineProps({{
  text: String,
  variant: {{ type: String, default: 'primary' }}
}})

const emit = defineEmits(['click'])
</script>

<template>
  <button @click="emit('click')" class="px-4 py-2 rounded-lg">
    {{{{ text }}}}
  </button>
</template>

Generate the {component_name} component now:
"""
    
    k2_llm_uri = os.getenv("K2_LLM_URI", "http://localhost:11434/v1")
    k2_llm_api_key = os.getenv("K2_LLM_API_KEY", "dummy-key")
    
    llm = ChatOpenAI(
        base_url=k2_llm_uri,
        api_key=k2_llm_api_key,
        model="MBZUAI-IFM/K2-Think",
        temperature=0.7,
    )
    
    logger.info(f"[EDITOR] Invoking LLM for component generation...")
    
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        vue_code = clean_vue_response(response.content)
        
        logger.info(f"[EDITOR] Successfully generated {component_name} component")
        return vue_code
        
    except Exception as e:
        logger.error(f"[EDITOR] Error generating component: {e}")
        raise


def clean_vue_response(raw_content: str) -> str:
    """
    Clean LLM response to extract just the Vue SFC code.
    Removes markdown code fences, think tags, etc.
    """
    # Remove <think> tags
    content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL)
    
    # Remove markdown code fences
    content = re.sub(r'```vue\n?', '', content)
    content = re.sub(r'```html\n?', '', content)
    content = re.sub(r'```\n?', '', content)
    
    # Extract from <answer> tags if present
    answer_match = re.search(r'<answer>(.*?)</answer>', content, re.DOTALL)
    if answer_match:
        content = answer_match.group(1)
    
    # Trim whitespace
    content = content.strip()
    
    # Ensure it starts with <script> or <template>
    if not (content.startswith('<script') or content.startswith('<template')):
        # Try to find the start
        script_idx = content.find('<script')
        template_idx = content.find('<template')
        
        if script_idx != -1 and template_idx != -1:
            start_idx = min(script_idx, template_idx)
            content = content[start_idx:]
        elif script_idx != -1:
            content = content[script_idx:]
        elif template_idx != -1:
            content = content[template_idx:]
    
    return content


# Keep old function for backward compatibility (will be removed later)
async def generate_code_llm(intent: str, context: str = "") -> str:
    """
    DEPRECATED: Old function that returns JSON.
    Use generate_vue_page() or generate_vue_component() instead.
    """
    logger.warning("[EDITOR] Using deprecated generate_code_llm, please update to new functions")
    
    # For now, just generate a simple page
    return await generate_vue_page("Component", intent, context)
