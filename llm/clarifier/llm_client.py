from pathlib import Path
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

MODEL_NAME = "MBZUAI-IFM/K2-Think"
BASE_URL = "https://llm-api.k2think.ai/v1"


def get_k2_client():
    """Initialize and return K2 Think OpenAI client."""
    api_key = os.getenv("K2_API_KEY")
    if not api_key:
        raise ValueError("K2_API_KEY not found in environment variables")
    
    return OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
        timeout=1200.0,
        max_retries=2
    )


def generate_clarification(intent: str, context: str) -> str:
    """
    Generate a Jarvis-style clarification reply based on intent and context.
    
    Args:
        intent: The ambiguous user request with explanation
        context: Previous actions/prompts for context
    
    Returns:
        A friendly, contextual clarification question in Jarvis style
    """
    client = get_k2_client()
    
    prompt = f"""You are JARVIS - a confident, witty AI assistant helping users build websites through voice commands. You're like the JARVIS from Iron Man: professional, helpful, with a touch of tech bro humor.

The user just said something ambiguous that needs clarification.

**User's Request (with explanation):**
{intent}

**Previous Context (what they were doing before):**
{context}

Your job: Ask a clarification question that's:
1. **Contextual** - Reference what they were just doing naturally
2. **Clear** - Get straight to the point about what's ambiguous
3. **Jarvis-style** - Confident, slightly witty, but professional when it matters
4. **Helpful** - Make it easy for them to answer

Examples of Jarvis-style responses:
- "Alright, just to make sure I've got this right - you want to change the submit button or the footer section? You mentioned both just now."
- "Okay, I need a quick clarification here. When you say 'make it bigger', are we talking about the text size, the button itself, or the whole container?"
- "Got it, but which 'that' are we working with? The image you just added or the header text from before?"

Keep it casual but clear. Reference the context naturally. Be helpful, not robotic.

Respond with ONLY the clarification question - no JSON, no extra formatting. Just your natural Jarvis reply."""

    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=False
    )
    
    content = response.choices[0].message.content.strip()
    
    # Handle potential XML tags from the model
    if "<answer>" in content and "</answer>" in content:
        content = content.split("<answer>")[1].split("</answer>")[0].strip()
    
    return content

