# config.py
import os
from pathlib import Path

# --- Server Config ---
# Use 0.0.0.0 to bind to all interfaces (required for Docker)
# Falls back to 127.0.0.1 for local development if HOST env var not set
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8098))

# --- Directory Config ---
# We assume this script is in the root, and 'src' is a subdir.
# (e.g., /app/run_server.py, /app/src/server.py)
BASE_DIR = Path(__file__).resolve().parent
INPUTS_DIR_NAME = "inputs"
OUTPUT_DIR_NAME = "../output/my-new-site"
STATIC_DIR_NAME = "static"
MANIFESTS_DIR_NAME = "manifests"

# --- Paths ---
AST_INPUT_DIR = BASE_DIR / INPUTS_DIR_NAME
OUTPUT_DIR = BASE_DIR / OUTPUT_DIR_NAME
STATIC_DIR = BASE_DIR / STATIC_DIR_NAME
MANIFESTS_DIR = BASE_DIR.parent / MANIFESTS_DIR_NAME
PROJECT_CONFIG_FILE = BASE_DIR / "project.json"

# --- Webhook ---
FRONTEND_REFRESH_WEBHOOK = "http://localhost:3000/api/refresh-iframe"

# --- V4: Default "Empty-Aware" Config ---
# This is the config that is loaded if project.json does not exist.
# It MUST have all keys that a "replace" patch might target,
# like globalStyles.
DEFAULT_PROJECT_CONFIG = {
  "projectName": "New GenAI Project",
  "pages": [],
  "globalStyles": ""
}