from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import DecideRequest, DecideResponse
from .planner import process_user_request

app = FastAPI(title="Planner Agent API", version="1.0.0")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/decide", response_model=DecideResponse)
async def decide(request: DecideRequest) -> DecideResponse:
    """
    Planner agent endpoint that classifies user intent and enriches prompts.
    
    Input:
    - sid: Session ID
    - text: User query
    
    Output:
    - step_id: Unique step identifier
    - step_type: Intent classification (edit/act/clarify)
    - intent: Enriched user query with explanation
    - context: Summarized context from previous prompts
    """
    try:
        response = process_user_request(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

