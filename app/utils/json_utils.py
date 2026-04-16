import json
import re


def extract_json(text: str) -> str:
    """
    Extract JSON object from LLM response.
    Handles cases where extra text surrounds JSON.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON object found in response")


def safe_json_loads(text: str):
    """
    Safely parse JSON with fallback cleaning.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = extract_json(text)
        return json.loads(cleaned)