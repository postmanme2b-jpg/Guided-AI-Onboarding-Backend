import json
from typing import Dict, Any
from openai import OpenAI
from config.prompts import IMPACT_PREVIEW_PROMPT

def get_impact_preview(problem_statement: str, challenge_type: str) -> str:
    """
    Analyzes the challenge context and returns a concise preview of the downstream
    impact of choosing a specific challenge type.

    Args:
        problem_statement: A string containing the problem statement from step 1.
        challenge_type: The selected challenge type (e.g., 'ideation', 'rtp').

    Returns:
        A string containing the AI-generated impact preview.
    """
    client = OpenAI()

    prompt = IMPACT_PREVIEW_PROMPT.format(
        problem_statement=problem_statement,
        challenge_type=challenge_type
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150,
        )

        preview_text = response.choices[0].message.content
        return preview_text.strip()
    except Exception as e:
        print(f"❌ An unexpected error occurred while getting impact preview: {e}")
        return "Could not generate an impact preview at this time."
