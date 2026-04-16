from openai import OpenAI
from app.config.settings import settings
import time


class LLMClient:
    """
    Wrapper around OpenAI client.
    Centralizes all LLM calls and adds retry logic.
    """

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        retries: int = 3,
        delay: float = 1.0
    ) -> str:
        """
        Generate text from LLM with retry logic.

        Args:
            prompt (str): Input prompt
            temperature (float): Creativity level
            retries (int): Number of retry attempts
            delay (float): Delay between retries (seconds)

        Returns:
            str: LLM response text
        """

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a precise language learning assistant. Always follow output instructions exactly."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )

                return response.choices[0].message.content

            except Exception as e:
                # Last attempt → raise error
                if attempt == retries - 1:
                    raise RuntimeError(f"LLM call failed after {retries} attempts: {e}")

                # Wait before retrying
                time.sleep(delay)