"""
server.py

Main entry point for the server app of the AI Agent Challenge Spec Generator.
This module sets up a FastAPI server with WebSocket support for real-time communication.
"""

import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import asyncio
from utils.input_handler import add_websocket_input_queue
from agent.architect import ChallengeArchitect
from agent.recommender import get_challenge_type_recommendations
from agent.impact_recommender import get_impact_preview
from agent.audience_recommender import get_audience_recommendations
from agent.submission_recommender import get_submission_recommendations
from agent.prize_recommender import get_prize_recommendations
from agent.timeline_recommender import get_timeline_recommendations
from agent.evaluation_recommender import get_evaluation_recommendations
from agent.communications_recommender import get_communications_recommendations
from agent.conflict_detector import detect_conflicts
import json
from typing import Dict, List, Any
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (for development; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_websockets: Dict[str, WebSocket] = {}
instances: Dict[str, ChallengeArchitect] = {}
messages: Dict[str, List[Dict[str, any]]] = {}

original_print_write = sys.stdout.write

def add_message(session_id: str, message: str, role: str = "assistant"):
    """
    Add a message to the session's message history.
    """
    if session_id not in messages:
        messages[session_id] = []
    messages[session_id].append({
        "role": role,
        "content": message,
        "timestamp": int(time.time())
    })

def custom_stdout_write(s):
    if ":" in s:
        session_id, message = s.split(":", 1)
        add_message(session_id, message)
        websocket = active_websockets.get(session_id)
        if websocket:
            try:
                asyncio.create_task(websocket.send_text(message))
            except RuntimeError:
                pass
        else:
            # If no WebSocket is active, just print to stdout
            original_print_write(s)
    else:
        original_print_write(s)

sys.stdout.write = custom_stdout_write
sys.stdout.reconfigure(encoding='utf-8')

# Pydantic models for API requests
class RecommendationRequest(BaseModel):
    problem_statement: str

class ImpactPreviewRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class AudienceRecommendationRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class SubmissionRecommendationRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class PrizeRecommendationRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class TimelineRecommendationRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class EvaluationRecommendationRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class CommunicationRecommendationRequest(BaseModel):
    problem_statement: str
    challenge_type: str

class ValidationRequest(BaseModel):
    challenge_data: Dict[str, Any]

class SchemaRequest(BaseModel):
    challenge_type: str
    step_id: str


@app.post("/api/recommendations")
async def get_ai_recommendations(request: RecommendationRequest):
    try:
        recommendations = get_challenge_type_recommendations(request.problem_statement)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/impact-preview")
async def get_ai_impact_preview(request: ImpactPreviewRequest):
    try:
        preview = get_impact_preview(request.problem_statement, request.challenge_type)
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/audience-recommendations")
async def get_ai_audience_recommendations(request: AudienceRecommendationRequest):
    try:
        recommendations = get_audience_recommendations(
            request.problem_statement,
            request.challenge_type
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submission-recommendations")
async def get_ai_submission_recommendations(request: SubmissionRecommendationRequest):
    try:
        recommendations = get_submission_recommendations(
            request.problem_statement,
            request.challenge_type
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prize-recommendations")
async def get_ai_prize_recommendations(request: PrizeRecommendationRequest):
    try:
        recommendations = get_prize_recommendations(
            request.problem_statement,
            request.challenge_type
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/timeline-recommendations")
async def get_ai_timeline_recommendations(request: TimelineRecommendationRequest):
    try:
        recommendations = get_timeline_recommendations(
            request.problem_statement,
            request.challenge_type
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluation-recommendations")
async def get_ai_evaluation_recommendations(request: EvaluationRecommendationRequest):
    try:
        recommendations = get_evaluation_recommendations(
            request.problem_statement,
            request.challenge_type
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/communications-recommendations")
async def get_ai_communications_recommendations(request: CommunicationRecommendationRequest):
    try:
        recommendations = get_communications_recommendations(
            request.problem_statement,
            request.challenge_type
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/validate-challenge")
async def validate_challenge_configuration(request: ValidationRequest):
    try:
        analysis = detect_conflicts(request.challenge_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get-schema-for-step")
async def get_schema_for_step(request: SchemaRequest):
    try:
        with open("config/platform_schema.json", "r") as f:
            schemas = json.load(f)

        # Robust matching for challenge_type (case-insensitive and strips whitespace)
        req_challenge_type = request.challenge_type.strip().lower()
        challenge_schema = next((s for s in schemas if s["challenge_type"].strip().lower() == req_challenge_type), None)

        if not challenge_schema:
            print(f"DEBUG: Challenge type '{req_challenge_type}' not found in schema.")
            raise HTTPException(status_code=404, detail=f"Challenge type '{req_challenge_type}' not found")

        # This mapping defines which fields from the schema belong to which step
        step_to_field_mapping = {
            "submission-requirements": ["deliverables"],
            "prize-configuration": ["prize_structure"],
            "timeline-milestones": ["timeline"]
            # Add other mappings here
        }

        required_fields = step_to_field_mapping.get(request.step_id, [])
        step_schema = {key: value for key, value in challenge_schema["fields"].items() if key in required_fields}

        return {"schema": step_schema}
    except Exception as e:
        # Log the actual error for debugging
        print(f"ERROR in /api/get-schema-for-step: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages")
async def get_messages(session: str = Query(...)):
    return {
        "session": session,
        "messages": messages.get(session, [])
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = websocket.query_params.get("session")
    if not session:
        await websocket.close(code=1008, reason="Session ID is required")
        return

    active_websockets[session] = websocket

    from utils.input_handler import websocket_input_queues
    input_queue = (websocket_input_queues or {}).get(session)
    if input_queue is None:
        input_queue = asyncio.Queue()
        add_websocket_input_queue(session, input_queue)

    if session not in instances:
        instances[session] = ChallengeArchitect(session=session)
        asyncio.create_task(instances[session].process_challenge())

    try:
        while True:
            data = await websocket.receive_text()
            try:
                content = json.loads(data).get("content")
            except json.JSONDecodeError:
                content = data
            if not content or content.strip() == "":
                await websocket.send_text("Error: Empty message received.")
                continue
            add_message(session, content, role="user")
            await input_queue.put(content)
    except WebSocketDisconnect:
        if active_websockets.get(session) == websocket:
            print(f"WebSocket disconnected for session: {session}")
            active_websockets.pop(session, None)
    except Exception as e:
        print(f"Error While listening from WebSocket. {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

