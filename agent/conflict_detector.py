import json
import traceback
from typing import Dict, Any, List
from openai import OpenAI
from config.prompts import CONFLICT_DETECTION_PROMPT

def detect_conflicts(challenge_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the complete challenge data to detect inconsistencies or potential issues.

    Args:
        challenge_data: A dictionary containing all the data gathered from the wizard steps.

    Returns:
        A dictionary containing a list of AI-detected warnings or suggestions.
    """
    try:
        client = OpenAI()

        # Serialize the challenge data into a readable string for the prompt
        data_summary = json.dumps(challenge_data, indent=2)

        prompt = CONFLICT_DETECTION_PROMPT.format(
            challenge_data_summary=data_summary
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are an expert challenge designer and helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        analysis = json.loads(response.choices[0].message.content)
        return analysis
    except Exception as e:
        print(f"❌ An unexpected error occurred while detecting conflicts: {e}")
        traceback.print_exc()
        return {"warnings": ["Could not perform AI validation at this time due to an error."]}
