from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, List

import numpy as np
from sentence_transformers import util

from .preprocess import TextPreprocessor
from .embeddings import EmbeddingModel
from .profile import UserProfileBuilder
from shared.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RecommenderConfig:
    top_k: int = 5


class NewsRecommender:
    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        preprocessor: Optional[TextPreprocessor] = None,
        profile_builder: Optional[UserProfileBuilder] = None,
        config: Optional[RecommenderConfig] = None,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel()
        self.preprocessor = preprocessor or TextPreprocessor()
        self.profile_builder = profile_builder or UserProfileBuilder()
        self.config = config or RecommenderConfig()

        logger.info(
            "NewsRecommender initialized",
            extra={"top_k": self.config.top_k},
        )

    def _clean_and_encode(self, texts: Sequence[str]) -> np.ndarray:
        logger.debug(
            "Cleaning and encoding texts",
            extra={"texts_count": len(texts)},
        )
        cleaned = self.preprocessor.clean_texts(texts)
        return self.embedding_model.encode(cleaned)

    def build_user_vector_from_texts(
        self,
        liked_texts: Sequence[str],
        disliked_texts: Optional[Sequence[str]] = None,
    ) -> np.ndarray:
        logger.debug(
            "build_user_vector_from_texts called",
            extra={
                "liked_count": len(liked_texts),
                "disliked_count": 0 if not disliked_texts else len(disliked_texts),
            },
        )

        if not liked_texts:
            logger.warning(
                "Empty liked_texts passed to build_user_vector_from_texts; returning empty vector"
            )
            return np.array([])

        try:
            liked_emb = self._clean_and_encode(liked_texts)
            if disliked_texts:
                disliked_emb = self._clean_and_encode(disliked_texts)
            else:
                disliked_emb = None

            user_vec = self.profile_builder.build(liked_emb, disliked_emb)
        except Exception:
            logger.exception("Failed to build user vector")
            raise

        logger.debug(
            "User vector built",
            extra={"dim": int(user_vec.shape[-1])},
        )
        return user_vec

    def rank_candidates(
        self,
        user_vector: np.ndarray,
        candidate_texts: Sequence[str],
        top_k: Optional[int] = None,
    ) -> Tuple[List[int], np.ndarray]:
        if user_vector.size == 0:
            logger.warning(
                "Empty user_vector passed to rank_candidates; returning empty result"
            )
            return [], np.array([])

        if not candidate_texts:
            logger.warning(
                "Empty candidate_texts passed to rank_candidates; returning empty result"
            )
            return [], np.array([])

        top_k = top_k or self.config.top_k

        logger.debug(
            "Ranking candidates",
            extra={
                "top_k": top_k,
                "candidates_count": len(candidate_texts),
            },
        )

        cand_emb = self._clean_and_encode(candidate_texts)

        user_vec_2d = user_vector.reshape(1, -1)
        cos_sim_matrix = util.cos_sim(user_vec_2d, cand_emb)  # (1, N)
        scores = cos_sim_matrix[0].cpu().numpy()              # (N,)

        sorted_indices = np.argsort(scores)[::-1]
        top_indices = sorted_indices[:top_k].tolist()

        logger.debug(
            "Candidates ranked",
            extra={"top_indices": top_indices},
        )

        return top_indices, scores
