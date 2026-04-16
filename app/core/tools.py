from langchain_core.tools import tool
from app.services.language_service import LanguageService

service = LanguageService()


@tool
def generate_practice_phrases(language: str, native_language: str, n: int = 10) -> dict:
    """
    Generate advanced CEFR C1-C2 phrases with translations and IPA.
    """
    result = service.get_practice_set(language, native_language)
    return result.model_dump()


@tool
def generate_pronunciation_feedback(
    target_text: str,
    user_attempt: str,
    issues: str
) -> dict:
    """
    Generate pronunciation feedback with a score from 1 to 5.
    """
    result = service.evaluate_attempt(
        target_text=target_text,
        user_attempt=user_attempt,
        issues=issues
    )
    return result.model_dump()