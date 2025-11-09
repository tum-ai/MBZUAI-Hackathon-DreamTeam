from pathlib import Path
import os
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

    http_client = httpx.Client(timeout=1200.0, follow_redirects=True)

    return OpenAI(
        base_url=BASE_URL,
        api_key=api_key,
        timeout=1200.0,
        max_retries=2,
        http_client=http_client,
    )


def generate_action(intent: str, context: str) -> str:
    """
    Generate an action based on intent and context.
    """
    client = get_k2_client()

    prompt = f"""You are an actor agent for a voice-first web development tool. Generate an action based on the intent and context.
    """
    messages = [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model=MODEL_NAME, messages=messages, stream=False
    )

    content = response.choices[0].message.content.strip()

    # Handle potential XML tags from the model
    if "<answer>" in content and "</answer>" in content:
        content = content.split("<answer>")[1].split("</answer>")[0].strip()

    return content
