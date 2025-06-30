import json
from typing import Dict, Any
from utils.input_handler import async_print

async def select_schema(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select the appropriate schema based on the challenge type defined in the scope.
    This function loads the schema from a JSON file and selects the one that matches the challenge type.
    If no type is specified, it defaults to 'development'.
    """

    type = state["scope"].get('type', 'development')

    await async_print(f"\n 🔎 Finding specification schema for challenge type: {type}...", session=state["session"])

    # If scope is defined, load the proper schema
    with open("config/platform_schema.json", "r") as f:
        schema_all = json.load(f)
        schema_selected = [item for item in schema_all if item["challenge_type"] == type]
        state["schema"] = schema_selected[0] if len(schema_selected) > 0 else schema_all[0]
        await async_print(f"🤖 Selected schema: \n```json\n{json.dumps(state['schema'], indent=2)}\n```", session=state["session"])

    return state