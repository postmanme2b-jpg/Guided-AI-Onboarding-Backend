# input_handler.py
import asyncio
import sys
from typing import Dict

websocket_input_queues: Dict[str, asyncio.Queue] = None

def add_websocket_input_queue(session: str, queue: asyncio.Queue):
    """
    Set the global WebSocket input queue for async input handling.
    This function is called by the server to initialize the queue.
    """
    global websocket_input_queues
    if websocket_input_queues is None:
        websocket_input_queues = {}
    websocket_input_queues[session] = queue

async def async_input(prompt: str = "", session: str = None) -> str:
    """
    Asynchronous input function that reads input from the WebSocket or standard input.
    If a session is provided, it will read from the WebSocket input queue.
    Otherwise, it will fall back to standard input for CLI mode.
    """
    if session is not None:
        websocket_input_queue = websocket_input_queues.get(session)
        if websocket_input_queue is None:
            raise RuntimeError("websocket_input_queue is not initialized for this session.")

        received_message = await websocket_input_queue.get()
        return received_message.strip()
    else:
        # Fallback to standard input for CLI mode (e.g., running main.py)
        return input(prompt).strip()

async def async_print(output, session: str = None, debug_message: bool = False):
    """
    Asynchronous print function that sends output to the WebSocket if a session exists.
    """
    # In server mode (session exists), send output via the custom print hook.
    # In CLI mode (no session), print directly to the console.
    if session is not None and debug_message is False:
        # This print statement is intercepted by the custom stdout in server.py
        print(session + ":" + output, flush=True)
        await asyncio.sleep(0.01)
    else:
        # For debug messages or when running in CLI mode
        print(f"Session-{session}: {output}", flush=True)
