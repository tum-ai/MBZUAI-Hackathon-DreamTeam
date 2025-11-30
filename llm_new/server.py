import logging
import sys
import time
import json
from typing import List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from llm.planner.models import PlanRequest, PlanResponse, AgentResult, TimingMetadata
from llm_new.agent import app as agent_app

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
