from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, List

import numpy as np
from sentence_transformers import util

from preprocess import TextPreprocessor
from embeddings import EmbeddingModel
from profile import UserProfileBuilder

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

    def _clean_and_encode(self, texts: Sequence[str]) -> np.ndarray:
        cleaned = self.preprocessor.clean_texts(texts)
        return self.embedding_model.encode(cleaned)
    
    def build_user_vector_from_texts(
             self,
        liked_texts: Sequence[str],
        disliked_texts: Optional[Sequence[str]] = None
    ) -> np.ndarray:
        liked_emb = self._clean_and_encode(liked_texts)

        if disliked_texts:
            disliked_emb = self._clean_and_encode(disliked_texts)
        else:
            disliked_emb = None

        user_vec = self.profile_builder.build(liked_emb, disliked_emb)
        return user_vec

    def rank_candidates(
        self,
        user_vector: np.ndarray,
        candidate_texts: Sequence[str],
        top_k: Optional[int] = None,
    ) -> Tuple[List[int], np.ndarray]:
        
        top_k = top_k or self.config.top_k

        cand_emb = self._clean_and_encode(candidate_texts)

        user_vec_2d = user_vector.reshape(1, -1)
        cos_sim_matrix = util.cos_sim(user_vec_2d, cand_emb)  # (1, N)
        scores = cos_sim_matrix[0].cpu().numpy()              # (N,)

        sorted_indices = np.argsort(scores)[::-1]
        top_indices = sorted_indices[:top_k].tolist()

        return top_indices, scores