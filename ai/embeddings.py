from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbendingConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize: bool = True
class EmbeddingModel:
    def __init__(self, config: Optional[EmbendingConfig] = None) -> None:
        self.config = config or EmbendingConfig()
        self._model: Optional[SentenceTransformer] = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.config.model_name)
        return self._model
    
    def encode(self, text: Sequence[str]) -> np.ndarray:
        model = self._load_model()
        embeddings: np.ndarray = model.encode(
            list(text),
            convert_to_numpy=True,
            normalize_embeddings=self.config.normalize,
        )
        return embeddings
