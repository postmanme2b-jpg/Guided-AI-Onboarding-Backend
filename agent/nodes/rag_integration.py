from typing import Dict, Any
from utils.input_handler import async_print

async def search_similar_challenge(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for similar past challenges based on the scope description.
    It retrieves challenges from a vector database and updates the state with the results.
    """

    await async_print(
        f"\n 🔎 Searching similar past challenges...",
        session=state["session"],
        debug_message=True
    )
    scope_description = state["scope"].get('description', 'development')

    # Search for similar challenges based on scope description
    from agent.architect import ChallengeArchitect
    instance = ChallengeArchitect()
    rag = instance.rag
    similar_challenges = rag.search_similar_challenges(scope_description)
    state["similar_challenges"] = similar_challenges

    await async_print(
        f"🤖 Found {len(similar_challenges)} similar challenges based on scope description.",
        session=state["session"],
        debug_message=True
    )
    await async_print("\nGenerating challenge specification...", session=state["session"], debug_message=True)

    return state