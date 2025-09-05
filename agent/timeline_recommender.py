import json
from datetime import datetime, timedelta
from typing import Dict, Any
from openai import OpenAI
from config.prompts import TIMELINE_RECOMMENDATION_PROMPT

def get_timeline_recommendations(problem_statement: str, challenge_type: str) -> Dict[str, Any]:
    """
    Analyzes the problem statement and challenge type to return AI-powered recommendations for the timeline and milestones.

    Args:
        problem_statement: A string containing the problem statement from step 1.
        challenge_type: The selected challenge type (e.g., 'ideation', 'rtp').

    Returns:
        A dictionary with recommendations for start date, end date, and key milestones.
    """
    try:
        client = OpenAI()

        prompt = TIMELINE_RECOMMENDATION_PROMPT.format(
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

        # Apply a new, robust date logic that ensures a staggered timeline
        today = datetime.today()
        launch_date = today + timedelta(days=1)
        recommendations["startDate"] = launch_date.strftime("%Y-%m-%d")

        milestones = recommendations.get("milestones", [])

        # Calculate the total duration and distribute milestones evenly
        total_days = 0
        if challenge_type == 'ideation':
            total_days = 14
        elif challenge_type == 'theoretical':
            total_days = 28
        elif challenge_type == 'rtp':
            total_days = 42
        elif challenge_type == 'erfp':
            total_days = 35
        elif challenge_type == 'prodigy':
            total_days = 21

        if total_days > 0 and len(milestones) > 1:
            step_days = total_days / (len(milestones) - 1)
            for i, milestone in enumerate(milestones):
                milestone_date = launch_date + timedelta(days=int(i * step_days))
                milestone["date"] = milestone_date.strftime("%Y-%m-%d")

        if milestones:
            recommendations["endDate"] = milestones[-1]["date"]
        else:
            recommendations["endDate"] = (launch_date + timedelta(days=total_days)).strftime("%Y-%m-%d")

        return recommendations
    except json.JSONDecodeError:
        print("❌ Failed to decode JSON from LLM response for timeline recommendations.")
        return {}
    except Exception as e:
        print(f"❌ An unexpected error occurred while getting timeline recommendations: {e}")
        return {}
