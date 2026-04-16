# ---------------------------
# IMPORTS
# ---------------------------
from fastapi import FastAPI, HTTPException, UploadFile, File
from openai import OpenAI
import json
import tempfile
import os

from app.services.language_service import LanguageService
from app.api.schemas import (
    PhraseRequest,
    FeedbackRequest,
    AgentRequest,
    AgentStructuredRequest,
    NaturalRequest
)
from app.core.agent import agent
from app.utils.parser import parse_user_input
from app.core.vector_store import store_phrases, retrieve_similar
from app.config.settings import settings
from app.evaluation.evaluator import evaluate_output  # NEW


# ---------------------------
# LANGSMITH CONFIG
# ---------------------------
if settings.LANGSMITH_TRACING:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY or ""
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT


# ---------------------------
# INITIALIZE
# ---------------------------
app = FastAPI(
    title="GenAI Language Coach API",
    description="Multimodal GenAI Language Learning System",
    version="4.0.0"
)

service = LanguageService()
client = OpenAI()


# ---------------------------
# ROOT
# ---------------------------
@app.get("/")
def root():
    return {"message": "GenAI Language Coach API is running"}


# ---------------------------
# DIRECT ENDPOINTS
# ---------------------------
@app.post("/generate")
def generate_phrases(request: PhraseRequest):
    try:
        phrases = service.get_practice_set(
            request.language,
            request.native_language
        )

        store_phrases(phrases.model_dump()["phrases"])

        return phrases.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def generate_feedback(request: FeedbackRequest):
    try:
        feedback = service.evaluate_attempt(
            request.target_text,
            request.user_attempt,
            request.issues
        )
        return feedback.model_dump()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# AGENT (FREE TEXT)
# ---------------------------
@app.post("/agent")
def run_agent(request: AgentRequest):
    try:
        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": request.message}
                ]
            }
        )

        raw_output = result["messages"][-1].content.strip()

        # Clean JSON
        if raw_output.startswith("```"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

        parsed_output = json.loads(raw_output)

        # Evaluation
        evaluation = evaluate_output(parsed_output)
        print("Evaluation:", evaluation)

        # Store phrases
        if "phrases" in parsed_output:
            store_phrases(parsed_output["phrases"])

        return {
            "status": "success",
            "data": parsed_output,
            "evaluation": evaluation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# AGENT (STRUCTURED BACKEND)  ✅ FULLY UPDATED
# ---------------------------
@app.post("/agent/structured")
def run_structured_agent(request: AgentStructuredRequest):
    try:
        # ---------------------------
        # BUILD PROMPT
        # ---------------------------
        if request.intent == "generate_phrases":
            if not request.language or not request.native_language:
                raise ValueError("language and native_language required")

            prompt = (
                f"Generate {request.n} advanced C1-C2 phrases in {request.language} "
                f"for a {request.native_language} speaker."
            )

        elif request.intent == "feedback":
            if not request.target_text or not request.user_attempt:
                raise ValueError("target_text and user_attempt required")

            prompt = (
                f"Target sentence: {request.target_text}\n"
                f"User attempt: {request.user_attempt}\n"
                f"Issues: {request.issues}\n"
                f"Provide pronunciation feedback with a score from 1 to 5."
            )

        else:
            raise ValueError("Invalid intent")

        # ---------------------------
        # AGENT CALL
        # ---------------------------
        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        raw_output = result["messages"][-1].content.strip()

        # ---------------------------
        # CLEAN JSON
        # ---------------------------
        if raw_output.startswith("```"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()

        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

        parsed_output = json.loads(raw_output)

        # ---------------------------
        # EVALUATION
        # ---------------------------
        evaluation = evaluate_output(parsed_output)
        print("Evaluation:", evaluation)

        # ---------------------------
        # VECTOR DB (RAG)
        # ---------------------------
        retrieved = None

        if request.intent == "generate_phrases":
            store_phrases(parsed_output["phrases"])

            query_text = parsed_output["phrases"][0]["sentence"]
            retrieved = retrieve_similar(query_text)

        # ---------------------------
        # RESPONSE
        # ---------------------------
        return {
            "status": "success",
            "intent": request.intent,
            "data": parsed_output,
            "evaluation": evaluation,
            "retrieval": retrieved
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# NATURAL LANGUAGE (LLM PARSING)
# ---------------------------
@app.post("/agent/natural")
def run_natural_agent(request: NaturalRequest):
    try:
        parsed = parse_user_input(request.message)

        intent = parsed.get("intent")
        language = parsed.get("language")
        native_language = parsed.get("native_language")
        target_text = parsed.get("target_text")
        user_attempt = parsed.get("user_attempt")
        issues = parsed.get("issues")

        if intent == "generate_phrases":
            structured_request = AgentStructuredRequest(
                intent="generate_phrases",
                language=language,
                native_language=native_language,
                n=5
            )

        elif intent == "feedback":
            structured_request = AgentStructuredRequest(
                intent="feedback",
                target_text=target_text,
                user_attempt=user_attempt,
                issues=issues
            )

        else:
            raise ValueError("Invalid intent")

        return run_structured_agent(structured_request)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------
# SPEECH → TEXT → AGENT
# ---------------------------
@app.post("/agent/speech")
async def speech_to_agent(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(contents)
            temp_path = tmp.name

        with open(temp_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio
            )

        text = transcript.text

        return run_natural_agent(NaturalRequest(message=text))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # ---------------------------
# PRONUNCIATION SCORING
# ---------------------------
@app.post("/pronunciation/score")
async def score_pronunciation(
    reference: UploadFile = File(...),
    user: UploadFile = File(...)
):
    try:
        from app.core.pronunciation import score_pronunciation_files

        ref_bytes = await reference.read()
        user_bytes = await user.read()

        result = score_pronunciation_files(ref_bytes, user_bytes)

        return {
            "status": "success",
            "score": result["score"],
            "similarity": result["similarity"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))