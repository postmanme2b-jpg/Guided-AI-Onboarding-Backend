from typing import Dict, Any
import json
from config.prompts import SPEC_DISCUSSION_PROMPT
from config.config import MAX_SPEC_CHANGES_ALLOWED

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from utils.input_handler import async_print, async_input

async def discuss_spec(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Discuss and refine the challenge specification based on user input and AI suggestions.
    This function allows for an iterative discussion to finalize the challenge spec.
    """

    from agent.architect import ChallengeArchitect
    llm = ChallengeArchitect().llm
    
    system_message = SystemMessage(
        content=SPEC_DISCUSSION_PROMPT.format(
            type=type,
            specification=str(state.get("spec", {})),
            reasoning_trace=str(state.get("reasoning_trace", [])),
            max_changes=MAX_SPEC_CHANGES_ALLOWED
        )
    )
    prompt = ChatPromptTemplate.from_messages([
        system_message,
        MessagesPlaceholder(variable_name="chat_history")
    ])
    messages = prompt.format_prompt(
        chat_history=state["discuss_spec_conversation"]
    ).to_messages()

    response = llm.invoke(messages)
    try:
        analysis = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback for robust operation
        analysis = {
            "completed": False,
        }

    should_complete = analysis.get("completed")
    ai_question = analysis.get("message")
    state["discuss_spec_conversation"].append(
        AIMessage(content=json.dumps(analysis))
    )
    spec = analysis.get("specification", {})
    reasoning_trace = analysis.get("reasoning_trace")
    if spec:
        await async_print("\n 📋 Specification updated:", session=state["session"])
        state["temp_spec"] = spec
        await async_print(json.dumps(spec, indent=2), session=state["session"])
    if reasoning_trace:
        await async_print("\n 🧠 Reasoning trace updated:", session=state["session"], debug_message=True)
        state["reasoning_trace"] = reasoning_trace
        await async_print(json.dumps(reasoning_trace, indent=2), session=state["session"], debug_message=True)

    if should_complete:
        state["spec"] = state.get("temp_spec") or state.get("spec", {})
        state["completed"] = True
        return state

    else:
        # Continue conversation with next question
        await async_print(f"\n🤖 AI: {ai_question}", session=state["session"])
        
        # Get next user response
        user_response = await async_input("\n🧑 You: ", session=state["session"])
        if not user_response:
            user_response = "I'm not sure, can you suggest something?"
        
        state["discuss_spec_conversation"].append(
            HumanMessage(content=user_response)
        )
        
        return state