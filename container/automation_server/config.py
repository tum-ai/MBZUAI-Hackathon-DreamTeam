# container_server/config.py
from pathlib import Path

# --- Container Server Config ---
CONTAINER_HOST = "127.0.0.1"
CONTAINER_PORT = 3000 # The port our main_frontend.html will talk to

# --- Vite/Vue App Config ---
# This is the path the container will watch
WATCH_PATH = Path(__file__).resolve().parent.parent.parent / "compiler" / "output" / "my-new-site"
VITE_PORT = 5173 # The port the compiled Vue app will run on
VITE_SERVER_PORT = 5173 # Alias for VITE_PORT used by automation server

# --- Callback Config ---
# This is the URL of your main Voice UI, to notify it of a refresh
# We will use a WebSocket connection instead, so this is just for reference
MAIN_FRONTEND_URL = "http://your-voice-ui.com"