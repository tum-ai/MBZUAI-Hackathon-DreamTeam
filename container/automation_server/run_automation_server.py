# automation_server/run_automation_server.py
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  # <-- Import CORS
from pydantic import BaseModel
import config
from browser_manager import BrowserManager
import atexit

app = FastAPI()

# --- ADD CORS MIDDLEWARE ---
# This tells the server to allow requests from other domains
# (like your ...usercontent.goog domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (be careful in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# --- END CORS MIDDLEWARE ---


# --- Global Browser Manager ---
# Create a single, shared instance of the manager
manager = BrowserManager()

@app.on_event("startup")
async def on_startup():
    """
    Start the BrowserManager (Vite subprocess + Playwright) on server startup.
    NOW ASYNC.
    """
    print("FastAPI startup: Initializing BrowserManager...")
    await manager.start()

@app.on_event("shutdown")
async def on_shutdown():
    """
    Ensure the manager is stopped when the FastAPI app shuts down.
    NOW ASYNC.
    """
    print("FastAPI shutdown: Stopping BrowserManager...")
    await manager.stop()
    
# --- Pydantic Models (for API validation) ---

class BrowserAction(BaseModel):
    """
    Defines the shape of an action, based on actionExecutor.js.
    """
    action: str
    targetId: str | None = None
    direction: str | None = None
    amount: int | None = None
    text: str | None = None

# --- API Endpoints ---

@app.post("/api/refresh-iframe")
async def refresh_iframe(background_tasks: BackgroundTasks):
    """
    Webhook endpoint to be called by the Compiler Server.
    Triggers a reload of the Vite server and Playwright instance.
    """
    print("Received /api/refresh-iframe request.")
    # Run in the background so we can return a 200 OK immediately
    # BackgroundTasks supports adding async functions.
    background_tasks.add_task(manager.handle_refresh_webhook)
    return {"message": "Refresh queued. Check server logs."}

@app.get("/api/browser/dom")
async def get_dom():
    """
    Gets the 'DOM snapshot' from the iframe (the 'eyes').
    NOW ASYNC.
    """
    print("Received /api/browser/dom request.")
    snapshot = await manager.get_dom_snapshot()
    return snapshot

@app.post("/api/browser/action")
async def execute_action(action: BrowserAction):
    """
    Executes an action on the iframe (the 'hands').
    NOW ASYNC.
    """
    print(f"Received /api/browser/action request: {action.model_dump_json()}")
    result = await manager.execute_browser_action(action.model_dump())
    return result
    
@app.get("/")
def read_root():
    return {"message": "Automation Server is running. Use the /api endpoints."}

if __name__ == "__main__":
    print(f"--- Starting Automation Server (V2 - Async) ---")
    print(f"--- Listening on: http://{config.AUTOMATION_SERVER_HOST}:{config.AUTOMATION_SERVER_PORT} ---")
    print(f"--- Managing Vue project in: {config.VUE_PROJECT_PATH} ---")
    print(f"--- Proxying Vite server on port: {config.VITE_SERVER_PORT} ---")
    
    uvicorn.run(
        app, 
        host=config.AUTOMATION_SERVER_HOST, 
        port=config.AUTOMATION_SERVER_PORT,
    )