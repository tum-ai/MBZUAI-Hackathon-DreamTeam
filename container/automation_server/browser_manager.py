# automation_server/browser_manager.py
import subprocess
import asyncio
import httpx
from threading import Thread
from playwright.async_api import async_playwright, Page, Browser, Locator, Error
import config

class BrowserManager:
    """
    Manages the Vite subprocess and the Playwright browser instance
    that connects to it.
    V3: Converted to full Async API to work with FastAPI/Uvicorn.
    """
    def __init__(self):
        self.vite_process: subprocess.Popen | None = None
        self.playwright = None
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.vite_url = f"http://localhost:{config.VITE_SERVER_PORT}"

    async def start(self):
        """
        Starts the Vite server subprocess and the Playwright browser.
        """
        print("Starting BrowserManager...")
        
        # Subprocess management is still sync, which is fine at startup.
        self._start_vite_server() 
        
        try:
            print("Launching Playwright (async)...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            
            print(f"Waiting for Vite server at {self.vite_url}...")
            await self._wait_for_vite()
            
            print(f"Navigating Playwright to {self.vite_url}")
            await self.page.goto(self.vite_url)
            print("BrowserManager started successfully.")
            
        except Exception as e:
            print(f"Error starting Playwright: {e}")
            await self.stop() # Cleanup on failure
            raise

    def _start_vite_server(self):
        """
        Starts the `npm run dev` subprocess.
        (This remains sync as subprocess.Popen is non-blocking)
        """
        if self.vite_process:
            print("Vite server already running.")
            return

        print(f"Starting Vite server in: {config.VUE_PROJECT_PATH}")
        # `npm install` is blocking, but it's a one-time setup cost at startup.
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=config.VUE_PROJECT_PATH,
                check=True,
                shell=True # Use shell=True for npm on Windows
            )
            print("`npm install` complete.")
        except Exception as e:
            print(f"Warning: `npm install` failed: {e}")

        # Popen is non-blocking and fine to run here.
        self.vite_process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--port", str(config.VITE_SERVER_PORT)],
            cwd=config.VUE_PROJECT_PATH,
            
            shell=True # Use shell=True for npm on Windows
        )
        print(f"Vite subprocess started with PID: {self.vite_process.pid}")

    async def _wait_for_vite(self, timeout=30):
        """Waits for the Vite server to be responsive (async)."""
        start_time = asyncio.get_event_loop().time()
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    response = await client.get(self.vite_url)
                    if response.status_code == 200:
                        print("Vite server is up!")
                        return
                except httpx.ConnectError:
                    pass # Server not up yet
                
                if (asyncio.get_event_loop().time() - start_time) > timeout:
                    raise TimeoutError("Timed out waiting for Vite server to start.")
                
                await asyncio.sleep(0.5)

    async def stop(self):
        """
        Stops the Playwright browser and kills the Vite server subprocess.
        """
        print("Stopping BrowserManager...")
        if self.browser:
            await self.browser.close()
            print("Playwright browser closed.")
        if self.playwright:
            await self.playwright.stop()
            print("Playwright instance stopped.")
        
        if self.vite_process:
            print(f"Terminating Vite subprocess (PID: {self.vite_process.pid})...")
            self.vite_process.terminate()
            self.vite_process.wait()
            print("Vite subprocess terminated.")
        
        self.vite_process = None
        self.browser = None
        self.page = None

    async def handle_refresh_webhook(self):
        """
        Handles the webhook from the compiler (async).
        Restarts the Vite server and reloads the Playwright page.
        """
        print("Webhook received! Rebuilding and refreshing...")
        
        # Stop everything
        if self.vite_process:
            self.vite_process.terminate()
            self.vite_process.wait()
            print("Old Vite process terminated.")
            
        # Restart Vite (npm install is sync, but that's ok)
        self._start_vite_server()
        await self._wait_for_vite()
        
        # Reload browser
        if self.page:
            print(f"Reloading Playwright page at {self.vite_url}")
            await self.page.reload()
            print("Page reloaded.")
        
        # Send callback to main frontend (async)
        try:
            async with httpx.AsyncClient() as client:
                await client.post(config.MAIN_FRONTEND_CALLBACK_URL, json={"status": "refreshed"}, timeout=3)
            print(f"Sent refresh callback to {config.MAIN_FRONTEND_CALLBACK_URL}")
        except Exception as e:
            print(f"Warning: Could not send final callback to main frontend: {e}")

    # --- Implemented "Eyes" (Async) ---
    
    async def get_dom_snapshot(self) -> dict:
        """
        Gets the 'DOM snapshot' from the iframe (async).
        """
        print("Getting DOM snapshot...")
        if not self.page:
            return {"error": "Page not loaded", "elements": []}

        try:
            locators = await self.page.locator('[data-nav-id]').all()
            snapshot = []
            viewport_height = self.page.viewport_size['height']
            
            print(f"[DOM Snapshot] Found {len(locators)} elements with data-nav-id")

            for locator in locators:
                nav_id = await locator.get_attribute('data-nav-id')
                if not nav_id:
                    continue

                rect = await locator.bounding_box()
                is_visible = await locator.is_visible()
                
                position_data = None
                is_in_viewport = False
                
                if rect:
                    is_in_viewport = (rect['y'] >= 0 and rect['y'] <= viewport_height)
                    position_data = {
                        "top": round(rect['y']),
                        "left": round(rect['x']),
                        "width": round(rect['width']),
                        "height": round(rect['height']),
                        "isInViewport": is_in_viewport
                    }

                snapshot.append({
                    "navId": nav_id,
                    "tagName": await locator.evaluate('el => el.tagName.toLowerCase()'),
                    "text": (await locator.text_content() or '').strip(),
                    "isVisible": is_visible,
                    "position": position_data,
                    "type": await locator.get_attribute('type') or None,
                    "className": await locator.get_attribute('class') or '',
                })

            return {
                "elements": snapshot,
                "timestamp": asyncio.get_event_loop().time(),
                "elementCount": len(snapshot),
                "source": "iframe-playwright"
            }
        except Error as e:
            print(f"Error during DOM snapshot: {e}")
            return {"error": f"Playwright error: {e}", "elements": []}

    # --- Implemented "Hands" (Async) ---

    async def _get_locator(self, target_id: str) -> Locator | None:
        """Helper to safely get a locator by nav-id (async check)."""
        if not self.page:
            return None
        locator = self.page.locator(f'[data-nav-id="{target_id}"]')
        if await locator.count() == 0:
            print(f"Action Error: Element {target_id} not found in iframe")
            return None
        return locator

    async def execute_browser_action(self, action: dict) -> dict:
        """
        Executes an action in the browser (async).
        """
        print(f"Executing browser action: {action}")
        if not self.page:
            return {"success": False, "message": "Page not loaded"}

        action_type = action.get('action')
        target_id = action.get('targetId')

        try:
            # --- Click Action ---
            if action_type == 'navigate': # 'navigate' is 'click' in actionExecutor.js
                locator = await self._get_locator(target_id)
                if not locator:
                    return {"success": False, "message": f"Element {target_id} not found"}
                
                await locator.click(timeout=5000)
                return {"success": True, "message": f"Clicked {target_id}", "source": "iframe-playwright"}

            # --- Scroll Action ---
            elif action_type == 'scroll':
                direction = action.get('direction')
                amount = action.get('amount', 300)
                
                if direction == 'up':
                    await self.page.mouse.wheel(0, -amount)
                elif direction == 'down':
                    await self.page.mouse.wheel(0, amount)
                elif direction == 'top':
                    await self.page.evaluate('window.scrollTo({ top: 0, behavior: "smooth" })')
                elif direction == 'bottom':
                    await self.page.evaluate('window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" })')
                else:
                    return {"success": False, "message": f"Unknown scroll direction: {direction}"}
                
                return {"success": True, "message": f"Scrolled {direction}", "source": "iframe-playwright"}

            # --- Scroll to Element ---
            elif action_type == 'scrollToElement':
                locator = await self._get_locator(target_id)
                if not locator:
                    return {"success": False, "message": f"Element {target_id} not found"}
                
                await locator.scroll_into_view_if_needed(timeout=5000)
                return {"success": True, "message": f"Scrolled to {target_id}", "source": "iframe-playwright"}

            # --- Type Action ---
            elif action_type == 'type':
                locator = await self._get_locator(target_id)
                if not locator:
                    return {"success": False, "message": f"Element {target_id} not found"}
                
                text_to_type = action.get('text', '')
                await locator.fill(text_to_type) # fill() is like 'clear' + 'type' and triggers events
                return {"success": True, "message": f"Typed '{text_to_type}' into {target_id}", "source": "iframe-playwright"}
            
            # --- Focus Action ---
            elif action_type == 'focus':
                locator = await self._get_locator(target_id)
                if not locator:
                    return {"success": False, "message": f"Element {target_id} not found"}
                
                await locator.focus()
                return {"success": True, "message": f"Focused on {target_id}", "source": "iframe-playwright"}
            
            # --- Clear Action ---
            elif action_type == 'clear':
                locator = await self._get_locator(target_id)
                if not locator:
                    return {"success": False, "message": f"Element {target_id} not found"}
                
                await locator.fill('') # fill with empty string
                return {"success": True, "message": f"Cleared {target_id}", "source": "iframe-playwright"}
            
            else:
                return {"success": False, "message": f"Unknown action type: {action_type}", "source": "iframe-playwright"}

        except Error as e:
            print(f"Error executing action {action_type} on {target_id}: {e}")
            return {"success": False, "message": f"Playwright error: {e}", "source": "iframe-playwright"}
        except Exception as e:
            print(f"Generic error executing action: {e}")
            return {"success": False, "message": f"Server error: {e}", "source": "iframe-playwright"}