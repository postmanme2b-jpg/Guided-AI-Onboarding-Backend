"""
server.py

Main entry point for the server app of the AI Agent Challenge Spec Generator.
This module sets up a FastAPI server with WebSocket support for real-time communication.
"""

import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from utils.input_handler import add_websocket_input_queue
from agent.architect import ChallengeArchitect
import json
from typing import Dict, List
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

@app.get("/messages")
async def get_messages(session: str = Query(...)):
    """
    HTTP GET endpoint to fetch messages for a given session ID.
    """
    return {
        "session": session,
        "messages": messages.get(session, [])
    }

# Endpoint WebSocket
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
        # Create a new input queue for this session
        input_queue = asyncio.Queue()
        add_websocket_input_queue(session, input_queue)

    if session not in instances:
        # Create a new instance of ChallengeArchitect for this session
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