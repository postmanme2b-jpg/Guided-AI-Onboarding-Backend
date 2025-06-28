from typing import Dict, List, Any, TypedDict, Optional
from typing_extensions import NotRequired
from langchain_core.messages import BaseMessage

class ChallengeState(TypedDict):
    """State representation for the Challenge Architect workflow.
    This defines the structure of the state used by the AI agents to manage
    """
    # Conversation history for each step
    discuss_scope_conversation: List[BaseMessage]
    generate_spec_conversation: List[BaseMessage]
    discuss_spec_conversation: List[BaseMessage]

    # Core challenge attributes
    scope: Dict[str, Any]
    schema: Dict[str, Any]
    similar_challenges: NotRequired[List[Dict[str, Any]]]
    spec: Dict[str, Any]
    temp_spec: NotRequired[Dict[str, Any]]
    
    suggestions_log: NotRequired[List[Dict[str, Any]]]
    reasoning_trace: List[Dict[str, Any]]
    completed: bool

    # Input files (mockups, screenshots, documents)
    files: List[str]

    # Results from vision analysis agent (optional workflow step)
    image_analysis: List[Dict[str, Any]]
