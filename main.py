#!/usr/bin/env python3
"""
Main entry point for the CLI app of the AI Agent Challenge Spec Generator.
"""

import sys
from agent.architect import ChallengeArchitect

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    try:

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