import os
import httpx
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

MODEL_NAME = "MBZUAI-IFM/K2-Think"
BASE_URL = "https://llm-api.k2think.ai/v1"


def get_k2_client():
    """Initialize and return K2 Think OpenAI client."""
    api_key = os.getenv("K2_API_KEY")
    if not api_key:
        raise ValueError("K2_API_KEY not found in environment variables")

    http_client = httpx.Client(timeout=1200.0, follow_redirects=True)

    return OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
        timeout=1200.0,
        max_retries=2,
        http_client=http_client,
    )


def generate_action(
    intent: str,
    context: str,
    system_prompt: str,
) -> str:
    """
    Generate an action based on intent and context.
    """
    client = get_k2_client()

    intent_text = intent.strip() if intent else ""
    context_text = context.strip() if context else ""
    context_text = context_text if context_text else "No additional context provided."

    user_content = (
        f'{intent_text}\n"""\n\n'
        f"Context:\n{context_text}\n\n"
        "Follow the instructions above and respond with ONLY the JSON action payload."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        stream=False,
    )

    content = response.choices[0].message.content.strip()

    # Handle potential XML tags from the model
    if "<answer>" in content and "</answer>" in content:
        content = content.split("<answer>")[1].split("</answer>")[0].strip()

    return content
