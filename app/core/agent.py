from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.core.tools import (
    generate_practice_phrases,
    generate_pronunciation_feedback,
)

# LLM
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)

# Agent
agent = create_agent(
    model=llm,
    tools=[
        generate_practice_phrases,
        generate_pronunciation_feedback,
    ],
    system_prompt=(
        "You are a multilingual language coach.\n\n"

        "IMPORTANT:\n"
        "You MUST return ONLY valid JSON.\n"
        "No explanations, no formatting, no extra text.\n\n"

        "For phrase generation:\n"
        "Return:\n"
        "{\n"
        '  "phrases": [\n'
        "    {\n"
        '      "sentence": "...",\n'
        '      "english_translation": "...",\n'
        '      "native_translation": "...",\n'
        '      "ipa": "..."\n'
        "    }\n"
        "  ]\n"
        "}\n\n"

        "For feedback:\n"
        "Return:\n"
        "{\n"
        '  "score": 1-5,\n'
        '  "feedback": "..."\n'
        "}\n"
    ),
)