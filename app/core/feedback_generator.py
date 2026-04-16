import json
from app.core.llm_client import LLMClient
from app.core.models import Feedback
from app.utils.json_utils import safe_json_loads

class FeedbackGenerator:
    def __init__(self):
        self.llm = LLMClient()

    def generate_feedback(self, target_text: str, user_attempt: str, issues: str):
        prompt = f"""
        Target sentence:
        {target_text}

        User attempt:
        {user_attempt}

        Detected issues:
        {issues}

        Return STRICT JSON:

        {{
          "score": 1-5,
          "feedback": "clear pronunciation advice"
        }}
        """

        raw_response = self.llm.generate(prompt)

        try:
            parsed = safe_json_loads(raw_response)
            return Feedback(**parsed)
        except Exception as e:
            raise ValueError(f"Failed to parse feedback: {e}\n{raw_response}")