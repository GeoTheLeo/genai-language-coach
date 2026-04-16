from app.services.language_service import LanguageService

service = LanguageService()

# Generate structured phrases
phrases = service.get_practice_set("Spanish", "German")

print("\nGenerated Phrases:\n")
for p in phrases.phrases:
    print(f"- {p.sentence}")
    print(f"  EN: {p.english_translation}")
    print(f"  DE: {p.native_translation}")
    print(f"  IPA: {p.ipa}\n")


# Structured feedback
feedback = service.evaluate_attempt(
    target_text="La decisión fue difícil.",
    user_attempt="La decision fue dificil.",
    issues="Missing accents and incorrect stress"
)

print("\nFeedback:\n")
print(f"Score: {feedback.score}")
print(f"Advice: {feedback.feedback}")