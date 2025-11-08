# run_server.py
import uvicorn
import config
from src.server import app

if __name__ == "__main__":
    # Ensure all directories exist on startup
    config.AST_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    config.STATIC_DIR.mkdir(parents=True, exist_ok=True)
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"--- Starting Generator Server (V4: Empty-Aware) ---")
    print(f"--- Running from: {config.BASE_DIR} ---")
    print(f"--- Monitoring project config: {config.PROJECT_CONFIG_FILE} ---")
    print(f"--- Monitoring ASTs in: {config.AST_INPUT_DIR} ---")
    print(f"--- Outputting to: {config.OUTPUT_DIR} ---")
    print(f"--- Refresh Webhook URL: {config.FRONTEND_REFRESH_WEBHOOK} ---")
    print(f"--- Server available at: http://{config.HOST}:{config.PORT} ---")
    
    # We pass the app as a string to enable reload
    # Note: 'reload=True' is great for development
    uvicorn.run("src.server:app", host=config.HOST, port=config.PORT, reload=True)