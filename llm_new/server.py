import logging
import sys
import time
import json
import shutil
from typing import List
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import FileResponse
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from llm.planner.models import PlanRequest, PlanResponse, AgentResult, TimingMetadata
from llm_new.agent import app as agent_app
from llm_new.session_manager import SessionManager

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Agent API (New)", version="1.0.0")

# Initialize SessionManager
session_manager = SessionManager(
    base_dir=Path("/tmp/vite-sessions"),
    template_dir=Path(__file__).parent / "templates" / "vite-vue-base",
    port_range=(3000, 4000),
    max_sessions=50
)

# Initialize FileManager
from llm_new.file_manager import FileManager
file_manager = FileManager(session_manager)

# Initialize tools with managers
from llm_new.tools import initialize_tools
initialize_tools(file_manager, session_manager)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/plan", response_model=PlanResponse)
async def plan(request: PlanRequest) -> PlanResponse:
    """
    Orchestration endpoint using LangGraph.
    """
    logger.info(f"Received /plan request for session: {request.sid}")
    start_time = time.time()
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=request.text)],
        "session_id": request.sid,
        "next_action": {},
        "results": []
    }
    
    try:
        # Run the graph
        final_state = await agent_app.ainvoke(initial_state)
        
        # Get results directly from state
        results_dicts = final_state.get('results', [])
        
        # Convert to AgentResult objects
        results = [
            AgentResult(**r) for r in results_dicts
        ]
        
        logger.info(f"Extracted {len(results)} results from state")
        
        total_duration = time.time() - start_time
        
        timing = TimingMetadata(
            planner_time_seconds=0.0, # Not separated
            total_agent_time_seconds=total_duration,
            total_time_seconds=total_duration,
            task_timings=[]
        )
        
        return PlanResponse(sid=request.sid, results=results, timing=timing)
        
    except Exception as e:
        logger.error(f"Error executing plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/plan-stream")
async def plan_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming plan execution.
    Sends step results as they complete instead of waiting for full plan.
    """
    await websocket.accept()
    logger.info("[WebSocket] Client connected")
    
    try:
        while True:
            # Receive plan request
            data = await websocket.receive_json()
            logger.info(f"[WebSocket] Received message: {data.get('type')}")
            
            if data.get("type") == "plan_request":
                # Extract request data
                request_id = data.get("requestId")
                session_id = data.get("sessionId")
                text = data.get("text")
                step_id = data.get("stepId")
                
                logger.info(f"[WebSocket] Processing plan request: {text[:50]}...")
                
                # Start streaming execution in background
                try:
                    await stream_plan_execution(
                        websocket,
                        request_id,
                        session_id,
                        text,
                        step_id
                    )
                except Exception as e:
                    logger.error(f"[WebSocket] Error during streaming: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "requestId": request_id,
                        "error": str(e)
                    })
                    
    except WebSocketDisconnect:
        logger.info("[WebSocket] Client disconnected")
    except Exception as e:
        logger.error(f"[WebSocket] Unexpected error: {e}")


async def stream_plan_execution(
    websocket: WebSocket,
    request_id: str,
    session_id: str,
    text: str,
    step_id: str = None
):
    """
    Stream plan execution results as each step completes.
    Uses LangGraph's astream() to get incremental updates.
    """
    start_time = time.time()
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=text)],
        "session_id": session_id,
        "next_action": {},
        "results": []
    }
    
    try:
        total_steps = 0
        
        # Stream graph execution
        async for event in agent_app.astream(initial_state):
            logger.info(f"[WebSocket] Graph event: {list(event.keys())}")
            
            # Check if executor node just completed
            if "executor" in event:
                state = event["executor"]
                
                # Check if we have new results
                if state.get("results"):
                    latest_result = state["results"][-1]
                    total_steps += 1
                    
                    logger.info(f"[WebSocket] Sending step {total_steps}: {latest_result['agent_type']}")
                    
                    # Send step completed message
                    await websocket.send_json({
                        "type": "step_completed",
                        "requestId": request_id,
                        "stepId": latest_result["step_id"],
                        "stepType": latest_result["agent_type"],
                        "intent": latest_result.get("intent", ""),
                        "context": latest_result.get("context", ""),
                        "result": latest_result["result"],
                        "executionTime": latest_result["execution_time_seconds"]
                    })
        
        # Send finish message
        total_duration = time.time() - start_time
        logger.info(f"[WebSocket] Plan finished: {total_steps} steps in {total_duration:.2f}s")
        
        await websocket.send_json({
            "type": "plan_finished",
            "requestId": request_id,
            "sessionId": session_id,
            "totalSteps": total_steps,
            "totalTime": total_duration
        })
        
    except Exception as e:
        logger.error(f"[WebSocket] Error in stream_plan_execution: {e}")
        import traceback
        traceback.print_exc()
        raise


# ============================================
# Session Management Endpoints
# ============================================

class CreateSessionRequest(BaseModel):
    session_id: str

@app.post("/sessions/create")
async def create_session(request: CreateSessionRequest):
    """
    Create a new Vite project for a session.
    Returns session info and Vite server URL.
    """
    try:
        session_id = request.session_id
        logger.info(f"[API] Creating session: {session_id}")
        session_info = await session_manager.create_session(session_id)
        
        return {
            "session_id": session_info.session_id,
            "vite_url": f"http://localhost:{session_info.vite_port}",
            "vite_port": session_info.vite_port,
            "created_at": session_info.created_at.isoformat(),
            "pages": session_info.pages_created
        }
    except Exception as e:
        logger.error(f"[API] Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}/exists")
async def session_exists(session_id: str):
    """Check if a session still exists"""
    exists = session_manager.session_exists(session_id)
    return {"exists": exists}


@app.get("/sessions/{session_id}/info")
async def get_session_info(session_id: str):
    """Get detailed session information"""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "vite_url": f"http://localhost:{session.vite_port}",
        "vite_port": session.vite_port,
        "created_at": session.created_at.isoformat(),
        "last_active": session.last_active.isoformat(),
        "pages": session.pages_created,
        "files_created": session.files_created
    }


@app.get("/sessions/{session_id}/export")
async def export_session(session_id: str):
    """
    Export session project as downloadable .zip file
    """
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Create zip archive
        zip_path = f"/tmp/{session_id}.zip"
        shutil.make_archive(
            zip_path.replace('.zip', ''),
            'zip',
            session.project_path
        )
        
        logger.info(f"[API] Exporting session {session_id} as zip")
        
        return FileResponse(
            zip_path,
            filename=f"my-website-{session_id}.zip",
            media_type="application/zip"
        )
    except Exception as e:
        logger.error(f"[API] Failed to export session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Manually delete a session"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        await session_manager.cleanup_session(session_id)
        logger.info(f"[API] Session {session_id} deleted")
        return {"deleted": True}
    except Exception as e:
        logger.error(f"[API] Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/stats")
async def get_sessions_stats():
    """Get statistics about all sessions"""
    return session_manager.get_session_stats()


# ============================================
# Startup/Shutdown Events
# ============================================

@app.on_event("startup")
async def startup_event():
    """Start background cleanup task on server startup"""
    import asyncio
    
    async def cleanup_loop():
        """Run cleanup every minute"""
        while True:
            await asyncio.sleep(60)
            try:
                logger.info("[Cleanup] Running inactive session cleanup")
                await session_manager.cleanup_inactive_sessions(timeout_seconds=300)
            except Exception as e:
                logger.error(f"[Cleanup] Error during cleanup: {e}")
    
    # Start cleanup task in background
    asyncio.create_task(cleanup_loop())
    logger.info("[Server] Background cleanup task started (5min timeout)")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up all sessions on server shutdown"""
    logger.info("[Server] Shutting down, cleaning up all sessions")
    session_ids = list(session_manager.sessions.keys())
    
    for session_id in session_ids:
        try:
            await session_manager.cleanup_session(session_id)
        except Exception as e:
            logger.error(f"[Shutdown] Error cleaning up {session_id}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
