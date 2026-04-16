# my "contract" between the LLM and my system
from pydantic import BaseModel, Field
from typing import List

class Phrase(BaseModel):
    """
    Represents a single generated phrase with metadata.
    """
    sentence: str = Field(..., description="Target language sentence")
    english_translation: str
    native_translation: str
    ipa: str


class PhraseSet(BaseModel):
    """
    Container for multiple phrases.
    """
    phrases: List[Phrase]


class Feedback(BaseModel):
    """
    Structured pronunciation feedback.
    """
    score: int = Field(..., ge=1, le=5)
    feedback: str