"""
Actor agent using Langchain patterns.
Wraps the existing actor logic with async Langchain-compatible interface.
"""
import os
import re
import json
import asyncio
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Import existing functionality
from llm.server import get_system_prompt, fetch_dom_snapshot
from llm.actor.actor import send_action_to_frontend


async def generate_action_llm(
    intent: str,
    context: str,
    session_id: str,
    step_id: str,
) -> str:
    """
    Generate an action using Langchain and K2-Think LLM.
    
    Args:
        intent: User's request with explanation
        context: Previous actions/prompts
        session_id: Session ID
        step_id: Step ID
        
    Returns:
        Action JSON string
    """
    # Fetch DOM snapshot to build system prompt
    dom_snapshot_response = await fetch_dom_snapshot()
    dom_snapshot = dom_snapshot_response.get("snapshot", {})
    
    # Get system prompt with dynamic sitemap
    system_prompt = get_system_prompt(dom_snapshot)
    
    # Prepare user message
    intent_text = intent.strip() if intent else ""
    context_text = context.strip() if context else "No additional context provided."
    
    user_content = (
        f'{intent_text}\n"""\n\n'
        f"Context:\n{context_text}\n\n"
        "Follow the instructions above and respond with ONLY the JSON action payload."
    )
    
    # Create LLM
    llm = ChatOpenAI(
        model="MBZUAI-IFM/K2-Think",
        base_url=os.environ.get("K2_LLM_URI", "https://llm-api.k2think.ai/v1"),
        api_key=os.environ.get("K2_LLM_API_KEY"),  # Use K2_LLM_API_KEY to match main agent
        temperature=0.1,
        timeout=1200.0,
        max_retries=2,
    )
    
    # Invoke LLM
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content)
    ]
    
    response = await llm.ainvoke(messages)
    content = response.content.strip()
    
    # Parse and clean response (same logic as original)
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    content = content.replace('</think>', '')
    
    if "<answer>" in content and "</answer>" in content:
        content = content.split("<answer>")[1].split("</answer>")[0].strip()
    elif "</answer>" in content:
        content = content.split("</answer>")[0].strip()
        content = content.replace('<answer>', '')
    
    # Clean up markdown code blocks
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
        
    # Extract JSON object using brace counting
    start_idx = content.find('{')
    if start_idx != -1:
        brace_count = 0
        for i, char in enumerate(content[start_idx:], start=start_idx):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    action_json = content[start_idx:i+1]
                    
                    # Also send action to frontend via WebSocket
                    try:
                        action_data = json.loads(action_json)
                        await send_action_to_frontend(action_data, session_id, step_id)
                    except Exception as e:
                        print(f"Warning: Could not send action to frontend: {e}")
                    
                    return action_json

    return content.strip()
