#!/usr/bin/env python3
"""
Main entry point for the CLI app of the AI Agent Challenge Spec Generator.
"""

import json
from agent.architect import ChallengeArchitect
from utils.input_handler import set_websocket_input_queue

async def main():
    try:

        global global_websocket_input_queue_instance # Deklarasikan bahwa kita akan memodifikasi global
        global_websocket_input_queue_instance = asyncio.Queue()
        set_websocket_input_queue(global_websocket_input_queue_instance)

        # Initialize the architect
        architect = ChallengeArchitect()
        
        # Process the challenge (will prompt for user input)
        result = await architect.process_challenge()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

import asyncio
if __name__ == "__main__":
    asyncio.run(main())