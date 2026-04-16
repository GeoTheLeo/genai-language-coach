from app.core.phrase_generator import PhraseGenerator
from app.core.feedback_generator import FeedbackGenerator

class LanguageService:
    def __init__(self):
        self.phrase_generator = PhraseGenerator()
        self.feedback_generator = FeedbackGenerator()

    def get_practice_set(self, language: str, native_language: str):
        return self.phrase_generator.generate_phrases(language, native_language)

    def evaluate_attempt(self, target_text: str, user_attempt: str, issues: str):
        return self.feedback_generator.generate_feedback(
            target_text,
            user_attempt,
            issues
        )