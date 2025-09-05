import json
from typing import Dict, Any, List
from openai import OpenAI
from config.prompts import CHALLENGE_TYPE_RECOMMENDATION_PROMPT

def get_challenge_type_recommendations(problem_description: str) -> List[Dict[str, Any]]:
    """
    Analyzes the problem description and returns AI-powered challenge type recommendations.
    This is a standalone function that can be called by a new API endpoint.
    It uses an LLM to generate challenge type recommendations based on the problem scope.

    Args:
        problem_description: A string containing the problem statement from step 1.

    Returns:
        A list of dictionaries, where each dictionary represents a recommended challenge type.
    """
    try:
        client = OpenAI()

        prompt = CHALLENGE_TYPE_RECOMMENDATION_PROMPT.format(
            problem_description=problem_description
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        recommendations_data = json.loads(response.choices[0].message.content)
        recommendations = recommendations_data.get("recommendations", [])

        if not isinstance(recommendations, list):
            print("❌ LLM did not return a list for recommendations. Returning empty.")
            return []

        return recommendations
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON from LLM response for challenge type recommendations.")
        return []
    except Exception as e:
        print(f"❌ An unexpected error occurred while getting recommendations: {e}")
        return []
