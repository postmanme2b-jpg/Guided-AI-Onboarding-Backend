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
    If running in a WebSocket server context, it will read from the WebSocket input queue.
    Otherwise, it will read from standard input.
    """
    if sys.argv[0] == "server.py" and session is not None:
        websocket_input_queue = websocket_input_queues.get(session)
        if websocket_input_queue is None:
            raise RuntimeError("websocket_input_queue is not initialized.")

        received_message = await websocket_input_queue.get()
        return received_message.strip()
    else:
        return input(prompt).strip()

async def async_print(output, session: str = None):
    """
    Asynchronous print function that sends output to the WebSocket.
    """
    if sys.argv[0] == "server.py" and session is not None:
        print(session + ":" + output, flush=True)
        await asyncio.sleep(0.01)
    else:
        print(output, flush=True)
