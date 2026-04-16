from pydantic import BaseModel


# ---------------------------
# Direct endpoints
# ---------------------------
class PhraseRequest(BaseModel):
    language: str
    native_language: str


class FeedbackRequest(BaseModel):
    target_text: str
    user_attempt: str
    issues: str


# ---------------------------
# Agent (free-form)
# ---------------------------
class AgentRequest(BaseModel):
    message: str


# ---------------------------
# Agent (structured) ← ADD THIS
# ---------------------------
class AgentStructuredRequest(BaseModel):
    intent: str
    language: str | None = None
    native_language: str | None = None
    target_text: str | None = None
    user_attempt: str | None = None
    issues: str | None = None
    n: int = 5

class NaturalRequest(BaseModel):
    message: str

class AudioRequest(BaseModel):
    # For now we simulate with file upload later
    placeholder: str = "audio"