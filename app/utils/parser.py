import json
import re
from openai import OpenAI

client = OpenAI()


def parse_user_input(message: str) -> dict:
    """
    Uses LLM to extract structured intent + entities from user input.

    Includes:
    - basic preprocessing (cleaning input)
    - strict JSON enforcement
    - robust parsing cleanup
    """

    # ---------------------------
    # PREPROCESSING (NEW)
    # ---------------------------
    cleaned = message.strip().lower()

    # ---------------------------
    # PROMPT
    # ---------------------------
    prompt = f"""
    Extract structured data from the user request.

    USER INPUT:
    "{cleaned}"

    RETURN ONLY VALID JSON (NO markdown, NO 'json', NO explanation):

    {{
      "intent": "generate_phrases" or "feedback",
      "language": "...",
      "native_language": "...",
      "target_text": null,
      "user_attempt": null,
      "issues": null
    }}
    """

    # ---------------------------
    # LLM CALL
    # ---------------------------
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    # ---------------------------
    # CLEAN RESPONSE (CRITICAL)
    # ---------------------------
    # Remove ```json or ```
    content = re.sub(r"```json|```", "", content).strip()

    # Remove leading "json"
    if content.startswith("json"):
        content = content[4:].strip()

    # ---------------------------
    # PARSE JSON
    # ---------------------------
    try:
        return json.loads(content)

    except Exception:
        raise ValueError(f"Failed to parse LLM output:\n{content}")