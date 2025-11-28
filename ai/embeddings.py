from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer
from shared.logging import *

logger = get_logger(__name__)

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
            logger.info(
                "Loading embedding model",
                extra={"model_name": self.config.model_name}
            )
            try:
                self._model = SentenceTransformer(self.config.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception:
                logger.exception(
                    "Failed to load embedding model",
                    extra={"model_name": self.config.model_name}
                )
                raise

        return self._model
    
    def encode(self, text: Sequence[str]) -> np.ndarray:

        logger.debug(
            "Encoding texts",
            extra={"texts_count": len(text), "normalize": self.config.normalize}
        )

        model = self._load_model()

        try:
            embeddings: np.ndarray = model.encode(
                list(text),
                convert_to_numpy=True,
                normalize_embeddings=self.config.normalize,
            )
        except Exception:
            logger.exception(
                "Failed to encode text",
                extra={"texts_count": len(text)}
            )
            raise

        logger.debug(
            "Successfully encoded texts",
            extra={"texts_count": len(text), "embedding_dim": embeddings.shape[-1]}
        )

        return embeddings
    