import json
import os
import uuid
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path(__file__).resolve().parent / "sessions"


def ensure_sessions_dir():
    """Ensure sessions directory exists."""
    SESSIONS_DIR.mkdir(exist_ok=True)


def get_session_file(sid: str) -> Path:
    """Get path to session file."""
    return SESSIONS_DIR / f"{sid}.json"


def load_session(sid: str) -> dict:
    """Load session data from file."""
    ensure_sessions_dir()
    session_file = get_session_file(sid)
    
    if not session_file.exists():
        return {"sid": sid, "prompts": []}
    
    with open(session_file, "r") as f:
        return json.load(f)


def save_session(sid: str, data: dict):
    """Save session data to file."""
    ensure_sessions_dir()
    session_file = get_session_file(sid)
    
    with open(session_file, "w") as f:
        json.dump(data, f, indent=2)


def get_previous_context(sid: str) -> str:
    """Get last 2 prompts from session as concatenated string."""
    session = load_session(sid)
    prompts = session.get("prompts", [])
    
    recent_prompts = prompts[-2:] if len(prompts) >= 2 else prompts
    
    context = " | ".join(recent_prompts)
    return context


def add_prompt_to_session(sid: str, text: str):
    """Add new prompt to session history (keep only last 2)."""
    session = load_session(sid)
    prompts = session.get("prompts", [])
    
    prompts.append(text)
    
    prompts = prompts[-2:]
    
    session["prompts"] = prompts
    save_session(sid, session)


def generate_step_id(sid: str) -> str:
    """Generate unique step ID based on session ID and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    namespace = uuid.NAMESPACE_DNS
    unique_id = uuid.uuid5(namespace, f"{sid}-{timestamp}")
    return str(unique_id)

