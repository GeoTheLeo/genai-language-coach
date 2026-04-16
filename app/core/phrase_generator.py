# Enforce JSON Output in Prompt
from app.core.llm_client import LLMClient
from app.core.models import PhraseSet
from app.utils.json_utils import safe_json_loads


class PhraseGenerator:
    """
    Generates advanced CEFR-level phrases with translations and IPA.
    """

    def __init__(self):
        self.llm = LLMClient()

    def generate_phrases(self, language: str, native_language: str, n: int = 10):
        """
        Generate structured phrases and validate them with Pydantic.
        Uses safe JSON parsing for robustness.
        """

        prompt = f"""
        Generate {n} advanced (C1-C2) sentences in {language}.

        The learner's native language is {native_language}.

        Return STRICT JSON in this format:

        {{
          "phrases": [
            {{
              "sentence": "...",
              "english_translation": "...",
              "native_translation": "...",
              "ipa": "..."
            }}
          ]
        }}

        IMPORTANT RULES:
        - "sentence" MUST be in {language}
        - "english_translation" MUST ALWAYS be in English
        - "native_translation" MUST ALWAYS be in {native_language}
        - DO NOT repeat English for native_translation UNLESS native_language is English
        - IPA must reflect the pronunciation of the sentence
        - DO NOT include explanations
        - DO NOT include markdown
        - RETURN ONLY VALID JSON
        """

        raw_response = self.llm.generate(prompt)

        try:
            parsed = safe_json_loads(raw_response)
            return PhraseSet(**parsed)

        except Exception as e:
            raise ValueError(
                f"Failed to parse LLM response.\n\nError: {e}\n\nRaw output:\n{raw_response}"
            )