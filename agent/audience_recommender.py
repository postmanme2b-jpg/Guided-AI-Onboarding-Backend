import json
import traceback
from typing import Dict, Any, List
from openai import OpenAI
from config.prompts import AUDIENCE_RECOMMENDATION_PROMPT

def get_audience_recommendations(problem_statement: str, challenge_type: str) -> Dict[str, Any]:
    """
    Analyzes the problem statement and challenge type to return AI-powered recommendations for audience and registration settings.

    Args:
        problem_statement: A string containing the problem statement from step 1.
        challenge_type: The selected challenge type (e.g., 'ideation', 'rtp').

    Returns:
        A dictionary with recommendations for audiences and participation types.
    """
    try:
        client = OpenAI()

        prompt = AUDIENCE_RECOMMENDATION_PROMPT.format(
            problem_statement=problem_statement,
            challenge_type=challenge_type
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        recommendations = json.loads(response.choices[0].message.content)
        return recommendations
    except json.JSONDecodeError as e:
        print(f"❌ Failed to decode JSON from LLM response for audience recommendations: {e}")
        return {}
    except Exception as e:
        print(f"❌ An unexpected error occurred while getting audience recommendations: {e}")
        traceback.print_exc()
        return {}

