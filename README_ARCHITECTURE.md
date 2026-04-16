# 🧠 System Architecture — GenAI Language Coach

## Overview
A multimodal AI system that supports:
- Text input
- Speech input
- Pronunciation evaluation

---

## Architecture Layers

### 1. Input Layer
- Text input (Streamlit)
- Audio input (.wav upload)

---

### 2. Processing Layer

#### LLM Agent (LangChain)
- Intent detection
- Structured output generation

#### Speech Processing
- OpenAI Whisper (transcription)

#### Pronunciation Model
- Wav2Vec2 embeddings
- Cosine similarity scoring

---

### 3. Retrieval Layer
- Vector DB (Chroma)
- Stores generated phrases
- Enables similarity-based retrieval

---

### 4. Output Layer
- Structured phrases
- IPA pronunciation
- Pronunciation score

---

## Data Flow

User → Streamlit → FastAPI → Agent / Model → Response → UI

---

## Design Decisions

- Structured prompts for consistency
- Modular endpoints for scalability
- Lightweight models for low latency
- Separation of UI and backend

---

## Future Work (Project 2)

- Real-time microphone input
- Phoneme-level scoring
- Adaptive learning system