import os
from dotenv import load_dotenv

# ---------------------------
# LOAD ENV VARIABLES
# ---------------------------
# Loads values from .env into environment
load_dotenv()


class Settings:
    """
    Central configuration class for the application.

    This keeps all environment variables in one place,
    making the system easier to manage and production-ready.
    """

    # ---------------------------
    # CORE API KEYS
    # ---------------------------
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    # ---------------------------
    # LANGSMITH CONFIG
    # ---------------------------
    LANGSMITH_API_KEY: str | None = os.getenv("LANGSMITH_API_KEY")

    # Default to "true" if set, otherwise False
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

    LANGSMITH_PROJECT: str = os.getenv(
        "LANGSMITH_PROJECT",
        "genai-language-coach"
    )


# ---------------------------
# SINGLETON INSTANCE!!
# ---------------------------
# This ensures consistent config across the app
settings = Settings()