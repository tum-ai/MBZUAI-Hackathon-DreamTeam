import logging
import sys
import time
from typing import List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
