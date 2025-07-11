import os
from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def _load_model(model_name: str = DEFAULT_MODEL_NAME) -> SentenceTransformer:
    """Load the sentence-transformer model once and cache it."""
    return SentenceTransformer(model_name)


def embed_texts(texts: List[str], *, normalize: bool = True) -> np.ndarray:
    """Return embeddings for a list of strings.

    Parameters
    ----------
    texts: List[str]
        Sentences / skills / bullets to embed.
    normalize: bool, default True
        Whether to L2-normalize the output vectors (cosine sim becomes dot-product).

    Returns
    -------
    np.ndarray  shape = (len(texts), dim)
    """
    if not texts:
        return np.empty((0, _load_model().get_sentence_embedding_dimension()))

    vecs = _load_model().encode(texts, normalize_embeddings=normalize)
    return np.asarray(vecs)


def aggregate_mean(vecs: np.ndarray) -> np.ndarray:
    """Return mean pooled vector. If vecs is empty, return zero vector."""
    if vecs.size == 0:
        dim = _load_model().get_sentence_embedding_dimension()
        return np.zeros(dim, dtype=np.float32)
    return vecs.mean(axis=0).astype(np.float32) 