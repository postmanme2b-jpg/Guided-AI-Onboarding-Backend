"""
server.py

Main entry point for the server app of the AI Agent Challenge Spec Generator.
This module sets up a FastAPI server with WebSocket support for real-time communication.
"""

import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.concurrency import asynccontextmanager
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from utils.input_handler import set_websocket_input_queue
from agent.architect import ChallengeArchitect
import json

app = FastAPI()

active_websockets: list[WebSocket] = []

original_print_write = sys.stdout.write

def custom_stdout_write(s):
    for websocket in active_websockets:
        try:
            asyncio.create_task(websocket.send_text(s))
        except RuntimeError:
            pass

sys.stdout.write = custom_stdout_write

# Endpoint WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    asyncio.create_task(ChallengeArchitect().process_challenge())

    try:
        while True:
            data = await websocket.receive_text()
            from utils.input_handler import websocket_input_queue
            await websocket_input_queue.put(json.loads(data).get("content") or data)
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        print(f"Error WebSocket: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global global_websocket_input_queue_instance
    global_websocket_input_queue_instance = asyncio.Queue()
    set_websocket_input_queue(global_websocket_input_queue_instance)
    yield

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)