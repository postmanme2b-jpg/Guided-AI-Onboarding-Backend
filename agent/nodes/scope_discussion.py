from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
from config.prompts import DEFINE_SCOPE_PROMPTS
from utils.input_handler import async_print, async_input

async def discuss_scope(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Discuss and define the scope of the challenge with the user.
    This function allows for an iterative discussion to finalize the challenge scope.
    """

    from agent.architect import ChallengeArchitect
    instance = ChallengeArchitect()
    llm = instance.llm
    
    system_message = SystemMessage(content=DEFINE_SCOPE_PROMPTS)
    prompt = ChatPromptTemplate.from_messages([
        system_message,
        MessagesPlaceholder(variable_name="chat_history")
    ])
    
    response = llm.invoke(
        prompt.format_prompt(
            chat_history=state["discuss_scope_conversation"]
        ).to_messages()
    )

    try:
        analysis = json.loads(response.content)
    except json.JSONDecodeError:
        analysis = {"completed": False, "message": "I'm having a little trouble processing that. Could you try rephrasing?"}

    should_complete = analysis.get("completed")
    ai_question = analysis.get("message", "")
    state["discuss_scope_conversation"].append(
        AIMessage(content=json.dumps(analysis))
    )

    # Standardize all outgoing messages to be JSON
    message_to_send = {"message": ai_question}

    if should_complete:
        work_scope = analysis.get("work_scope", {})
        suggestions = analysis.get("suggestions", [])
        
        # Add completion data to the final message
        message_to_send["message"] = "Excellent! We have decided the scope of the challenge. Here's the summary:"
        message_to_send["work_scope"] = work_scope
        message_to_send["completed"] = True

        await async_print(json.dumps(message_to_send), session=state["session"])
        
        state["scope"] = work_scope
        state["suggestions_log"] = suggestions
        return state
    else:
        await async_print(json.dumps(message_to_send), session=state["session"])

        user_response = await async_input("\n🧑 You: ", session=state["session"])
        
        if not user_response:
            user_response = "No, that's all for now."
        
        state["discuss_scope_conversation"].append(
            HumanMessage(content=user_response)
        )
        
        return state
