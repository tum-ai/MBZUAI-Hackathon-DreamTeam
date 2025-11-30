"""
Clarifier agent using Langchain patterns.
"""
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


async def generate_clarification_llm(intent: str, context: str) -> str:
    """
    Generate a Jarvis-style clarification using Langchain and K2-Think LLM.
    
    Args:
        intent: The ambiguous user request with explanation
        context: Previous actions/prompts for context
        
    Returns:
        A friendly, contextual clarification question in Jarvis style
    """
    # Load prompt from external file
    prompt_path = Path(__file__).parent / "prompts" / "clarifier_prompt.md"
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt_template = f.read()
    except Exception as e:
        print(f"Error reading clarifier prompt: {e}")
        system_prompt_template = "You are a helpful AI assistant. Ask for clarification."
    
    # Build user prompt
    user_prompt = f"""**User's Request (with explanation):**

{intent}

**Previous Context (what they were doing before):**

{context}
"""
    
    # Create LLM
    llm = ChatOpenAI(
        model="MBZUAI-IFM/K2-Think",
        base_url=os.environ.get("K2_LLM_URI", "https://llm-api.k2think.ai/v1"),
        api_key=os.environ.get("K2_LLM_API_KEY"),  # Use K2_LLM_API_KEY to match main agent
        temperature=0.7,  # Slightly higher for more natural responses
        timeout=1200.0,
        max_retries=2,
    )
    
    # Combine system prompt template with user input
    full_prompt = system_prompt_template + "\n\n" + user_prompt
    
    messages = [HumanMessage(content=full_prompt)]
    
    response = await llm.ainvoke(messages)
    content = response.content.strip()
    
    # Handle potential XML tags from the model
    if "<answer>" in content and "</answer>" in content:
        content = content.split("<answer>")[1].split("</answer>")[0].strip()

    return content
