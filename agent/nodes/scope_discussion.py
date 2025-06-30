from typing import Dict, List, Any
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
        # Fallback for robust operation
        analysis = {
            "completed": False,
        }
        
    # COMPLETION LOGIC: Determine if conversation should continue
    should_complete = analysis.get("completed")
    ai_question = analysis.get("message", "")
    state["discuss_scope_conversation"].append(
        AIMessage(content=json.dumps(analysis))
    )

    if should_complete:
        # Signal completion with summary of gathered information
        await async_print("\n🎉 Excellent! We have decided the scope of the challenge.", session=state["session"])
        await async_print("📋 Here's the summary:", session=state["session"])

        work_scope = analysis.get("work_scope", {})
        suggestions = analysis.get("suggestions", [])
        
        # Display gathered information for user confirmation
        await async_print(json.dumps({"challenge_type": work_scope.get('type', 'No type provided')}), session=state["session"])
        await async_print(json.dumps({"description": work_scope.get('description', 'No description provided')}), session=state["session"])
        await async_print(json.dumps({"suggestion_reasoning": analysis.get('suggestions', 'No reasoning provided')}), session=state["session"])
        
        state["scope"] = work_scope
        state["suggestions_log"] = suggestions

        return state
    else:
        # Continue conversation with next question
        
        await async_print(f"\n🤖 AI: {ai_question}", session=state["session"])
        
        # Get next user response
        user_response = await async_input("\n🧑 You: ", session=state["session"])
        
        if not user_response:
            user_response = "No, that's all for now."
        
        state["discuss_scope_conversation"].append(
            HumanMessage(content=user_response)
        )
        
        return state
    