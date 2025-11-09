from pathlib import Path
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

MODEL_NAME = "MBZUAI-IFM/K2-Think"
BASE_URL = "https://llm-api.k2think.ai/v1"


def get_k2_client():
    """Initialize and return K2 Think OpenAI client."""
    api_key = os.getenv("K2_API_KEY")
    if not api_key:
        raise ValueError("K2_API_KEY not found in environment variables")
    
    import httpx
    http_client = httpx.Client(timeout=1200.0)
    
    return OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
        http_client=http_client,
        max_retries=2
    )


def split_tasks(user_text: str, previous_context: str = "") -> dict:
    """
    Split user request into multiple tasks if needed.
    Returns dict with: tasks (list), context_summary (str)
    """
    client = get_k2_client()
    
    needs_summary = len(previous_context) > 100
    
    if needs_summary:
        prompt = f"""You are a planner agent for a voice-first web development tool. Analyze the user's request and detect if it contains multiple tasks.

User request: "{user_text}"

Previous context (last 2 prompts): "{previous_context}"

Your job:
1. Detect if the request contains multiple distinct tasks (e.g., "scroll down, click submit, and make it orange" is 3 tasks)
2. Split into individual tasks in chronological order
3. For each task, classify as:
   - "act" (perform action): ANY user interaction with existing UI elements
     Examples: scroll, click, navigate, hover, **fill in form fields**, enter text, type, press keys, check boxes, submit forms, select dropdowns, etc.
   - "edit" (modify website structure/style): changing the website code, design, or content
     Examples: change colors, add new components, modify layout, style changes, create elements, etc.
   - "clarify" (need more information): vague or ambiguous requests
   IMPORTANT: If user is interacting with existing form fields/inputs (filling, typing, entering data), it's ALWAYS "act", NOT "edit"
4. Add clear explanation for each task
5. Provide a concise summary of the previous context (it's longer than 100 characters)

Respond with ONLY valid JSON in this exact format:
{{
    "tasks": [
        {{
            "text": "the task text",
            "step_type": "edit" | "act" | "clarify",
            "explanation": "detailed explanation for next agent"
        }}
    ],
    "context_summary": "concise summary of previous context"
}}

If there's only one task, return a single-item array."""
    else:
        prompt = f"""You are a planner agent for a voice-first web development tool. Analyze the user's request and detect if it contains multiple tasks.

User request: "{user_text}"

Previous context (last 2 prompts): "{previous_context}"

Your job:
1. Detect if the request contains multiple distinct tasks (e.g., "scroll down, click submit, and make it orange" is 3 tasks)
2. Split into individual tasks in chronological order
3. For each task, classify as:
   - "act" (perform action): ANY user interaction with existing UI elements
     Examples: scroll, click, navigate, hover, **fill in form fields**, enter text, type, press keys, check boxes, submit forms, select dropdowns, etc.
   - "edit" (modify website structure/style): changing the website code, design, or content
     Examples: change colors, add new components, modify layout, style changes, create elements, etc.
   - "clarify" (need more information): vague or ambiguous requests
   IMPORTANT: If user is interacting with existing form fields/inputs (filling, typing, entering data), it's ALWAYS "act", NOT "edit"
4. Add clear explanation for each task

Respond with ONLY valid JSON in this exact format:
{{
    "tasks": [
        {{
            "text": "the task text",
            "step_type": "edit" | "act" | "clarify",
            "explanation": "detailed explanation for next agent"
        }}
    ]
}}

If there's only one task, return a single-item array."""

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
        
        if not needs_summary:
            result["context_summary"] = ""
        
        return {
            "tasks": result.get("tasks", [{"text": user_text, "step_type": "clarify", "explanation": "Could not parse tasks"}]),
            "context_summary": result.get("context_summary", "")
        }
    except (json.JSONDecodeError, IndexError) as e:
        # Fallback: treat as single task
        return {
            "tasks": [{
                "text": user_text,
                "step_type": "clarify",
                "explanation": f"Could not parse tasks. Original request: {user_text}"
            }],
            "context_summary": ""
        }


#def classify_intent(user_text: str, previous_context: str = "") -> dict:
    """
    Classify user intent and enrich with explanation.
    Returns dict with: step_type, explanation, context_summary
    """
    client = get_k2_client()
    
    needs_summary = len(previous_context) > 100
    
    if needs_summary:
        # prompt = f"""You are a planner agent for a voice-first web development tool. Analyze the user's request and respond with a JSON object.
        #
        # User request: "{user_text}"
        #
        # Previous context (last 2 prompts): "{previous_context}"
        #
        # Tasks:
        # 1. Classify the intent as one of: "edit" (modify website), "act" (perform action like scroll/click/navigate), or "clarify" (need more information)
        # 2. Add a clear explanation that helps the next agent understand what needs to be done
        # 3. Provide a concise summary of the previous context (it's longer than 100 characters)
        #
        # Respond with ONLY valid JSON in this exact format:
        # {{
        #     "step_type": "edit" | "act" | "clarify",
        #     "explanation": "detailed explanation for next agent",
        #     "context_summary": "concise summary of previous context"
        # }}"""
        prompt = ""
    else:
        # prompt = f"""You are a planner agent for a voice-first web development tool. Analyze the user's request and respond with a JSON object.
        #
        # User request: "{user_text}"
        #
        # Previous context (last 2 prompts): "{previous_context}"
        #
        # Tasks:
        # 1. Classify the intent as one of: "edit" (modify website), "act" (perform action like scroll/click/navigate), or "clarify" (need more information)
        # 2. Add a clear explanation that helps the next agent understand what needs to be done
        #
        # Respond with ONLY valid JSON in this exact format:
        # {{
        #     "step_type": "edit" | "act" | "clarify",
        #     "explanation": "detailed explanation for next agent"
        # }}"""
        prompt = ""

    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    
    content = response.choices[0].message.content.strip()
    
    #  <think> and <answer> tags to be parsed
    try:
        if "<answer>" in content and "</answer>" in content:
            content = content.split("<answer>")[1].split("</answer>")[0].strip()
        elif "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        if not needs_summary:
            result["context_summary"] = ""
        
        return result
    except (json.JSONDecodeError, IndexError) as e:
        return {
            "step_type": "clarify",
            "explanation": f"Could not parse intent. Original request: {user_text}",
            "context_summary": ""
        }
