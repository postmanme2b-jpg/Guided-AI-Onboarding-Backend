import json
from typing import Dict, Any, List
from openai import OpenAI
from config.prompts import EVALUATION_RECOMMENDATION_PROMPT

def get_evaluation_recommendations(problem_statement: str, challenge_type: str) -> Dict[str, Any]:
    """
    Analyzes the problem statement and challenge type to return AI-powered recommendations for evaluation criteria.

    Args:
        problem_statement: A string containing the problem statement from step 1.
        challenge_type: The selected challenge type (e.g., 'ideation', 'rtp').

    Returns:
        A dictionary with recommendations for a scoring model and a set of criteria.
    """
    try:
        client = OpenAI()

        prompt = EVALUATION_RECOMMENDATION_PROMPT.format(
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
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON from LLM response for evaluation recommendations.")
        return {}
    except Exception as e:
        print(f"❌ An unexpected error occurred while getting evaluation recommendations: {e}")
        return {}
