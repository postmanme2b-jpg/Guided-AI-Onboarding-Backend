from typing import Dict, Any
import json
from config.prompts import SPEC_GENERATION_PROMPT

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from utils.input_handler import async_print, async_input

async def generate_spec(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a challenge specification based on the provided scope and schema.
    """

    from agent.architect import ChallengeArchitect
    llm = ChallengeArchitect().llm
    
    scope = state.get("scope", {})
    type = scope.get('type', 'development')
    description = scope.get('description', 'No scope provided')

    system_message = SystemMessage(
        content=SPEC_GENERATION_PROMPT.format(
            type=type,
            scope=description,
            schema=str(state.get("schema", {})),
            similar_challenges=str(state.get("similar_challenges", []))
        )
    )

    prompt = ChatPromptTemplate.from_messages([
        system_message,
        MessagesPlaceholder(variable_name="chat_history")
    ])
    
    response = llm.invoke(
        prompt.format_prompt(
            chat_history=state["generate_spec_conversation"]
        ).to_messages()
    )
    try:
        analysis = json.loads(response.content)
    except json.JSONDecodeError:
        # Fallback for robust operation
        analysis = {
            "completed": False,
        }
    
    should_complete = analysis.get("completed")
    ai_question = analysis.get("message")
    state["generate_spec_conversation"].append(
        AIMessage(content=json.dumps(analysis))
    )

    if should_complete:
        spec = analysis.get("specification", {})
        reasoning_trace = analysis.get("reasoning_trace", [])
        state["spec"] = spec
        state["reasoning_trace"] = reasoning_trace

        await async_print("\n🎉 Excellent! We have generated the challenge specification. Here's the formatted specification:", session=state["session"])
        await async_print(json.dumps(spec, indent=2), session=state["session"])

        await async_print("\n 🧠 Reasoning trace:", session=state["session"], debug_message=True)
        await async_print(json.dumps(reasoning_trace, indent=2), session=state["session"], debug_message=True)

    # Continue conversation with next question
    await async_print(f"\n🤖 AI: {ai_question}", session=state["session"])
    
    # Get next user response
    user_response = await async_input("\n🧑 You: ", session=state["session"])
    
    if not user_response:
        user_response = "I'm not sure, can you suggest something?"
    
    if should_complete:
        state["discuss_spec_conversation"].append(
            HumanMessage(content=user_response)
        )
    else:
        state["generate_spec_conversation"].append(
            HumanMessage(content=user_response)
        )
    
    return state