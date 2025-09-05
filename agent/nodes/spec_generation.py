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
        analysis = { "completed": False }
    
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

        final_message = {
            "message": ai_question or "Excellent! We have generated the challenge specification. Here's the formatted specification:",
            "specification": spec,
            "reasoning_trace": reasoning_trace,
            "completed": True
        }
        await async_print(json.dumps(final_message), session=state["session"])

    else:
        # If the conversation is not complete, send the AI's question back to the user.
        message_to_user = {
            "message": ai_question
        }
        await async_print(json.dumps(message_to_user), session=state["session"])

    # Always wait for user input after sending a message
    user_response = await async_input("\n🧑 You: ", session=state["session"])
    
    if not user_response:
        user_response = "Looks good, let's proceed."
    
    if should_complete:
        state["discuss_spec_conversation"].append(
            HumanMessage(content=user_response)
        )
    else:
        state["generate_spec_conversation"].append(
            HumanMessage(content=user_response)
        )
    
    return state

