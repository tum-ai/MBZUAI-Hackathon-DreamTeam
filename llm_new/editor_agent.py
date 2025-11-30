"""
Editor agent using Langchain patterns.
"""
import os
import json
import re
import logging
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger(__name__)


async def generate_code_llm(intent: str, context: str, current_ast: dict = None) -> str:
    """
    Generate UI component code using Langchain and K2-Think LLM.
    
    Args:
        intent: User's request with explanation
        context: Previous actions/prompts for context
        current_ast: Current page AST (optional, for edit actions)
        
    Returns:
        Component JSON string
    """
    logger.info(f"[EDITOR] Generating code for intent: {intent[:100]}...")
    
    # Load prompt from external file
    prompt_path = Path(__file__).parent / "prompts" / "editor_prompt.md"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    except Exception as e:
        logger.error(f"Error reading editor prompt: {e}")
        system_prompt = "You are a UI component generator. Generate valid JSON components."
    
    # Build user prompt with clearer instructions
    ast_section = ""
    if current_ast:
        ast_str = json.dumps(current_ast, indent=2)
        ast_section = f"""

**CURRENT_PAGE_AST**:
```json
{ast_str}
```"""
    
    user_prompt = f"""**USER REQUEST**: {intent}

**CONTEXT**: {context}{ast_section}

**TASK**: Generate a component that fulfills the user's request.

{system_prompt}

**CRITICAL**: Output ONLY the JSON object. No markdown, no explanations, no code fences. Just the raw JSON starting with {{ and ending with }}.

**Example Output**:
{{"id": "my-button", "type": "Button", "props": {{"text": "Click Me", "style": {{"padding": "10px"}}}}, "slots": {{}}}}

Generate the component JSON now:
"""
    
    # Create LLM
    llm = ChatOpenAI(
        model="MBZUAI-IFM/K2-Think",
        base_url=os.environ.get("K2_LLM_URI", "https://llm-api.k2think.ai/v1"),
        api_key=os.environ.get("K2_LLM_API_KEY"),  # Use K2_LLM_API_KEY to match main agent
        temperature=0.1,
        timeout=1200.0,
        max_retries=2,
    )
    
    messages = [HumanMessage(content=user_prompt)]
    
    logger.info("[EDITOR] Invoking LLM...")
    response = await llm.ainvoke(messages)
    content = response.content.strip()
    
    logger.info(f"[EDITOR] Raw LLM response length: {len(content)}")
    logger.info(f"[EDITOR] Raw LLM response (first 200 chars): {content[:200]}")
    
    # Parse response handling <think> and <answer> tags
    # Strip <think> tags completely
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    
    if "<answer>" in content and "</answer>" in content:
        content = content.split("<answer>")[1].split("</answer>")[0].strip()
        logger.info("[EDITOR] Extracted content from <answer> tags")
    elif "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
        logger.info("[EDITOR] Extracted content from ```json code block")
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        logger.info("[EDITOR] Extracted content from ``` code block")
    
    logger.info(f"[EDITOR] Cleaned content length: {len(content)}")
    logger.info(f"[EDITOR] Cleaned content (first 200 chars): {content[:200]}")
    
    # Validate it's valid JSON
    try:
        component = json.loads(content)
        
        # Validate required fields
        if "id" not in component:
            component["id"] = "generated-component"
            logger.warning("[EDITOR] Added missing 'id' field")
        if "type" not in component:
            component["type"] = "Box"
            logger.warning("[EDITOR] Added missing 'type' field")
        
        result = json.dumps(component)
        logger.info(f"[EDITOR] Successfully generated component: {result[:100]}...")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"[EDITOR] JSON parsing failed: {e}")
        logger.error(f"[EDITOR] Content that failed to parse: {content}")
        
        # Return minimal valid component with error info
        error_component = {
            "id": "error-component",
            "type": "Box",
            "props": {},
            "slots": {},
            "error": f"Could not parse component: {str(e)}",
            "raw_content": content[:500]  # Include snippet of what was returned
        }
        return json.dumps(error_component)
