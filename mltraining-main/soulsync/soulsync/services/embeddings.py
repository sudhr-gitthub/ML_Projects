from __future__ import annotations

import os
import numpy as np
from functools import lru_cache

MODEL_NAME_DEFAULT = "sentence-transformers/all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_embedder():
    """Lazy-load embedder model."""
    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMBED_MODEL_ID", MODEL_NAME_DEFAULT)
    return SentenceTransformer(model_name)


def embed_text(text: str) -> np.ndarray:
    emb = get_embedder().encode([text], normalize_embeddings=True)
    return np.array(emb[0], dtype=np.float32)


def serialize_vector(vec: np.ndarray) -> bytes:
    vec = np.asarray(vec, dtype=np.float32)
    return vec.tobytes()


def deserialize_vector(blob: bytes, dim: int) -> np.ndarray:
    arr = np.frombuffer(blob, dtype=np.float32)
    if dim and arr.size != dim:
        return arr
    return arr
