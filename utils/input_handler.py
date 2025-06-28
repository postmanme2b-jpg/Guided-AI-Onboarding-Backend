# input_handler.py
import asyncio
import sys

websocket_input_queue: asyncio.Queue = None

def set_websocket_input_queue(queue: asyncio.Queue):
    """
    Set the global WebSocket input queue for async input handling.
    This function is called by the server to initialize the queue.
    """
    global websocket_input_queue
    websocket_input_queue = queue

async def async_input(prompt: str = "") -> str:
    """
    Asynchronous input function that reads input from the WebSocket or standard input.
    If running in a WebSocket server context, it will read from the WebSocket input queue.
    Otherwise, it will read from standard input.
    """
    if sys.argv[0] == "server.py":
        if websocket_input_queue is None:
            raise RuntimeError("websocket_input_queue is not initialized.")

        received_message = await websocket_input_queue.get()
        return received_message.strip()
    else:
        return input(prompt).strip()

async def async_print(output):
    """
    Asynchronous print function that sends output to the WebSocket.
    """

    print(output, flush=True)
    if sys.argv[0] == "server.py":
        await asyncio.sleep(0.01)