import numpy as np
import tempfile
import librosa
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import torch

# Load model once (important for performance)
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")


def load_audio_from_bytes(audio_bytes):
    """
    Load audio from bytes and resample to 16kHz (required for Wav2Vec2).
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        temp_path = tmp.name

    audio, sr = librosa.load(temp_path, sr=16000)
    return audio


def extract_embedding(audio):
    """
    Convert audio waveform into embedding using Wav2Vec2.
    """
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooling over time dimension
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding


def cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def score_pronunciation_files(ref_bytes, user_bytes):
    """
    Main scoring function used by FastAPI endpoint.
    """

    ref_audio = load_audio_from_bytes(ref_bytes)
    user_audio = load_audio_from_bytes(user_bytes)

    ref_emb = extract_embedding(ref_audio)
    user_emb = extract_embedding(user_audio)

    similarity = float(cosine_similarity(ref_emb, user_emb))

    # Convert similarity to 1–5 score
    score = round(similarity * 5, 2)

    return {
        "similarity": similarity,
        "score": score
    }