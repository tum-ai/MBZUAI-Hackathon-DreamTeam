# container_server/run_server.py
import uvicorn
import asyncio
import subprocess
import time
import httpx
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import List

import config

# --- FastAPI App ---
app = FastAPI()

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New client connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected: {websocket.client}")

    async def broadcast(self, message: str):
        """Send a message to all connected clients."""
        print(f"Broadcasting message to {len(self.active_connections)} client(s): {message}")
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error sending message to client: {e}")
                self.active_connections.remove(connection)

manager = ConnectionManager()

class SubprocessManager:
    """Manages the Vite subprocess."""
    def __init__(self, path: Path, port: int):
        self.path = path
        self.port = port
        self.process: subprocess.Popen | None = None
        self.needs_npm_install = False
        # --- MODIFICATION: Store the main event loop ---
        self.loop: asyncio.AbstractEventLoop | None = None 
        # --- MODIFICATION: Timer handle is simpler than a task ---
        self.debounce_timer: asyncio.TimerHandle | None = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Receives the main event loop from the startup event."""
        self.loop = loop

    def start_vite_server(self):
        if self.process:
            print("Vite server already running.")
            return

        if not self.path.exists():
            print(f"Error: Watch path does not exist: {self.path}")
            print("Please run the compiler server first to generate the site.")
            return
            
        # Run `npm install` if needed
        if self.needs_npm_install:
            print("`package.json` changed. Running `npm install`...")
            try:
                subprocess.run(
                    ["npm", "install"],
                    cwd=self.path,
                    check=True,
                    shell=True # Use shell=True for npm on Windows
                )
                print("`npm install` complete.")
                self.needs_npm_install = False # Reset flag
            except Exception as e:
                print(f"Warning: `npm install` failed: {e}")

        # Start the dev server
        print(f"Starting Vite server in: {self.path}")
        self.process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--port", str(self.port)],
            cwd=self.path,
            shell=True # Use shell=True for npm on Windows
        )
        print(f"Vite subprocess started with PID: {self.process.pid}")

    def stop_vite_server(self):
        if self.process:
            print(f"Stopping Vite subprocess (PID: {self.process.pid})...")
            self.process.terminate()
            self.process.wait()
            print("Vite subprocess stopped.")
            self.process = None

    async def wait_for_vite(self, timeout=30):
        """Waits for the Vite server to be responsive."""
        print(f"Waiting for Vite server at http://localhost:{self.port}...")
        start_time = time.time()
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    response = await client.get(f"http://localhost:{self.port}")
                    if response.status_code == 200:
                        print("Vite server is up!")
                        return True
                except (httpx.ConnectError, httpx.ReadTimeout):
                    pass # Server not up yet
                
                if time.time() - start_time > timeout:
                    print("Error: Timed out waiting for Vite server.")
                    return False
                
                await asyncio.sleep(0.5)

    async def _handle_restart(self):
        """The debounced restart function."""
        # This function is now guaranteed to run on the main event loop
        print("Debounce timer fired. Restarting server...")
        self.stop_vite_server()
        self.start_vite_server()
        
        # Wait for server to be ready and notify clients
        if await self.wait_for_vite():
            await manager.broadcast("refresh")
        else:
            await manager.broadcast("error")
            
    def _run_restart_threadsafe(self):
        """
        A thread-safe wrapper that's called by the timer.
        Its only job is to create the async task on the main loop.
        """
        if not self.loop:
            print("Error: Event loop not set in SubprocessManager.")
            return
        
        print("Debounce wrapper: Creating _handle_restart task...")
        self.debounce_timer = None # Clear the timer handle
        self.loop.create_task(self._handle_restart())

    def schedule_restart(self, needs_install=False):
        """
        Schedules a debounced restart from a different thread.
        This function IS called from the Watchdog thread.
        """
        if not self.loop:
            print("Error: Event loop not set, cannot schedule restart.")
            return
            
        if needs_install:
            self.needs_npm_install = True
        
        # If a timer is already running, cancel it (thread-safe)
        if self.debounce_timer:
            self.loop.call_soon_threadsafe(self.debounce_timer.cancel)
        
        # Start a new timer using call_later (thread-safe)
        print("File change detected. Scheduling server restart in 2 seconds...")
        self.debounce_timer = self.loop.call_later(
            2, # 2-second delay
            self._run_restart_threadsafe # Function to call in the main thread
        )

class WatcherEventHandler(FileSystemEventHandler):
    """Listens for file changes and triggers the subprocess manager."""
    def __init__(self, sp_manager: SubprocessManager):
        self.sp_manager = sp_manager
        # --- NEW: Define files/folders to ignore ---
        self.ignore_dirs = ['.vite', 'node_modules']
        self.ignore_files = ['package-lock.json']
        self.ignore_prefixes = ['vite.config.js.timestamp']
        
        # --- NEW: Define files/extensions to explicitly WATCH for ---
        self.watch_files = ['package.json', 'index.html', 'vite.config.js', 'automation_agent.js']
        self.watch_extensions = ['.vue', '.js']


    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        file_name = file_path.name
        
        # --- NEW: Smart filtering logic ---
        try:
            # 1. Check if the file is in an ignored directory
            if any(part in file_path.parts for part in self.ignore_dirs):
                # print(f"Ignoring change in ignored directory: {file_path}")
                return

            # 2. Check if the file itself is ignored
            if file_name in self.ignore_files:
                # print(f"Ignoring change to lockfile: {file_name}")
                return
            
            # 3. Check for ignored prefixes (like Vite's cache files)
            if any(file_name.startswith(prefix) for prefix in self.ignore_prefixes):
                # print(f"Ignoring change to temp file: {file_name}")
                return
                
            # 4. Check if this is a file we explicitly watch
            is_watched_file = file_name in self.watch_files
            is_watched_extension = file_path.suffix in self.watch_extensions and 'src' in file_path.parts
            
            if is_watched_file or is_watched_extension:
                print(f"Change detected in important file: {file_name}")
                # Check if it's package.json
                if file_name == "package.json":
                    self.sp_manager.schedule_restart(needs_install=True)
                else:
                    self.sp_manager.schedule_restart(needs_install=False)
            else:
                # This file is not in our ignore list but not explicitly watched.
                # We'll ignore it to be safe.
                # print(f"Ignoring change to non-trigger file: {file_name}")
                pass

        except Exception as e:
            print(f"Error in file watcher: {e}")
        # --- End of new logic ---

# --- Global Managers ---
sp_manager = SubprocessManager(path=config.WATCH_PATH, port=config.VITE_PORT)
event_handler = WatcherEventHandler(sp_manager)
observer = Observer()

@app.on_event("startup")
def on_startup():
    """Start the Vite server and the file watcher on app startup."""
    print("FastAPI startup...")
    
    # --- MODIFICATION: Get the loop and pass it to the manager ---
    loop = asyncio.get_running_loop()
    sp_manager.set_event_loop(loop)
    
    # 1. Start the Vite server for the first time
    sp_manager.start_vite_server()
    # 2. Start watching for file changes
    observer.schedule(event_handler, str(config.WATCH_PATH), recursive=True)
    observer.start()
    print(f"File watcher started on: {config.WATCH_PATH}")

@app.on_event("shutdown")
def on_shutdown():
    """Stop the Vite server and file watcher on app shutdown."""
    print("FastAPI shutdown...")
    observer.stop()
    observer.join()
    sp_manager.stop_vite_server()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for the main frontend to listen for refresh commands."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return {"message": "Container Server is running."}

if __name__ == "__main__":
    print(f"--- Starting Container Server (V1) ---")
    print(f"--- Listening on: http://{config.CONTAINER_HOST}:{config.CONTAINER_PORT} ---")
    
    uvicorn.run(app, host=config.CONTAINER_HOST, port=config.CONTAINER_PORT)