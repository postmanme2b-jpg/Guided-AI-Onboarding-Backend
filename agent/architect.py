"""
agent/architect.py

This module defines the ChallengeArchitect class, which orchestrates a multi-agent workflow for generating structured challenge specifications from natural language descriptions. The architecture leverages LangGraph to coordinate specialized AI agent nodes, each responsible for a distinct phase of the challenge specification process.

Agents in the workflow:
- Scope Discussion Agent: Interactively clarifies and refines the initial challenge description with the user.
- Schema Selection Agent: Selects the most appropriate schema template based on the clarified scope.
- RAG Integration Agent: Searches for similar challenges using retrieval-augmented generation to provide relevant context and inspiration.
- Specification Generation Agent: Drafts a structured challenge specification from the gathered information and selected schema.
- Specification Discussion Agent: Iteratively reviews and refines the generated specification with the user to ensure completeness and correctness.

Key Features:
- Modular agent nodes for each workflow stage, enabling extensibility and clear separation of concerns.
- Conditional transitions between nodes, allowing dynamic, context-aware progression through the workflow.
- Integration with OpenAI LLMs and RAG for enhanced reasoning and retrieval capabilities.
- Asynchronous, interactive user input and output handling for conversational experiences.
- Comprehensive state management to track conversation history, suggestions, reasoning, and generated specifications.

This architecture enables the automated, interactive, and explainable transformation of user goals into detailed, structured challenge specifications suitable for downstream use.
"""
import json
from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import os

from agent.nodes.scope_discussion import discuss_scope
from agent.nodes.schema_selection import select_schema
from agent.nodes.rag_integration import search_similar_challenge
from agent.nodes.spec_generation import generate_spec
from agent.nodes.spec_discussion import discuss_spec

from utils.rag import RAGHelper

from utils.schema import ChallengeState
from utils.input_handler import async_print, async_input

class ChallengeArchitect:
    """
    AI Agent Copilot for Structured Challenge Specification
    
    This class orchestrates a multi-agent workflow that converts natural language
    challenge descriptions into structured specifications through interactive AI conversation.
    """

    def __init__(self, session: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Challenge Architect with LLM models and workflow configuration.
        
        Args:
            api_key: OpenAI API key for LLM access
            session: Optional session identifier for WebSocket communication
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.session = session
        self.llm = ChatOpenAI(model="gpt-4.1", api_key=self.api_key, temperature=0.5)
        self.rag = RAGHelper()

        # Build the LangGraph workflow
        self.workflow = self._build_workflow()
                
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for the challenge architect agent.
        
        This creates a state machine with conditional transitions between specialized AI agents.
        Each node represents a different AI agent with specific capabilities.
        """
        
        # Define the state graph with initial state structure
        workflow = StateGraph(ChallengeState)
        
        # Add specialized AI agent nodes to the graph
        workflow.add_node("discuss_scope", discuss_scope)      # Interactive conversation agent
        workflow.add_node("select_schema", select_schema)        # Schema selection agent
        workflow.add_node("search_similar_challenge", search_similar_challenge)  # Similar challenge search agent
        workflow.add_node("generate_spec", generate_spec)          # Specification generation agent
        workflow.add_node("discuss_spec", discuss_spec)

        def should_continue_discussing_scope(state):
            """
            Determine if we should continue discussing scope or move to schema matching.
            This implements the conditional workflow logic for the initial scope discussion.
            """
            # If we have enough information, skip to template matching
            if not state["scope"]:
                return "discuss_scope"
            else:
                return "select_schema"

        def should_continue_generating_spec(state):
            """
            Determine if we should continue generating the specification or finish.
            This implements the conditional workflow logic for the spec generation.
            """
            # If we have enough information, finish the spec generation
            if not state["spec"]:
                return "generate_spec"
            else:
                return "discuss_spec"  # Proceed to discuss spec
        def should_continue_discussing_spec(state):
            """
            Determine if we should continue discussing the specification or finish.
            This implements the conditional workflow logic for the spec discussion.
            """
            if state["completed"]:
                return "end"
            else:
                return "discuss_spec"

        workflow.add_conditional_edges(
            "discuss_scope",
            should_continue_discussing_scope,
            {
                "discuss_scope": "discuss_scope",          # Continue scope discussion
                "select_schema": "select_schema"          # Select schema based on scope
            }
        )
        workflow.add_edge("select_schema", "search_similar_challenge")
        workflow.add_edge("search_similar_challenge", "generate_spec")
        workflow.add_conditional_edges(
            "generate_spec",
            should_continue_generating_spec,
            {
                "generate_spec": "generate_spec",
                "discuss_spec": "discuss_spec",
            }
        )
        workflow.add_conditional_edges(
            "discuss_spec",
            should_continue_discussing_spec,
            {
                "discuss_spec": "discuss_spec",          # Continue scope discussion
                "end": END
            }
        )
        
        # Set the entry point
        workflow.set_entry_point("discuss_scope")
        
        return workflow.compile()

    async def print_section(self, title, content, emoji = "📋", debug_message = False):
        """Helper function to print formatted sections"""
        await async_print(f"\n{emoji} {title}", session=self.session, debug_message=debug_message)
        # await async_print("=" * (len(title) + 4), session=self.session)
        await async_print(content, session=self.session, debug_message=debug_message)

    async def process_challenge(self) -> Dict[str, Any]:
        """
        Process a challenge request and generate a structured spec through interactive AI conversation.
        
        This is the main entry point that orchestrates the entire multi-agent workflow.
        
        Returns:
            Dict containing generated specification, reasoning trace, and conversation history
        """
        
        # Get prompt from input_data or ask user for input
        await async_print(
"""## 🚀 Welcome to the AI Challenge Spec Generator! 🚀 
Please describe your goal for the challenge.
Examples:
- 'I want to build a food delivery app for students'
- 'Create a marketplace for freelance designers'
- 'Build an AI model to predict stock prices'
- 'Design a mobile game for kids'""", session=self.session)
        
        user_prompt = await async_input("Your challenge description: ", session=self.session)
        if not user_prompt:
            user_prompt = "I want to build a food delivery app for students"  # fallback
            await async_print(f"Using default prompt: {user_prompt}", session=self.session, debug_message=True)
                    
        # Store the prompt in the class variable so nodes can access it
        initial_prompt = user_prompt
        
        # Initialize the state for the agent workflow
        initial_state = {
            "session": None, 
            "discuss_scope_conversation": [],
            "generate_spec_conversation": [],
            "discuss_spec_conversation": [],

            "scope": {},
            "schema": {},
            "similar_challenges": [],
            "spec": {},
            "temp_spec": {},

            "suggestions_log": [],
            "reasoning_trace": [],
            "completed": False,
        }
        
        if self.session:
            # If a session is provided, set it in the initial state
            initial_state["session"] = self.session
        initial_state["discuss_scope_conversation"].append(
            HumanMessage(content=initial_prompt)
        )
        # Execute the LangGraph workflow
        final_state = await self.workflow.ainvoke(initial_state)

        await async_print("## 🎉 CHALLENGE SPECIFICATION GENERATION IS COMPLETED! 🎉", session=self.session)

        # Show the generated specification
        await self.print_section(
            "Generated Challenge Specification", 
            json.dumps(final_state["spec"], indent=2),
            "📋"
        )
        await self.print_section(
            "Scope Suggestions Log",
            json.dumps(final_state["suggestions_log"], indent=2),
            "💡",
            debug_message=True
        ) 
        await self.print_section(
            "Specification Reasoning Trace", 
            json.dumps(final_state["reasoning_trace"], indent=2),
            "🧠",
            debug_message=True
        )

        # Return the final spec with reasoning trace
        return {
            "spec": final_state["spec"],
            "reasoning_trace": final_state["reasoning_trace"],
            # "conversation_history": serializable_conversation
        }