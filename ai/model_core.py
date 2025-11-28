from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import numpy as np

from .recommender import NewsRecommender

_recommender: Optional[NewsRecommender] = None


def get_recommender() -> NewsRecommender:
    global _recommender
    if _recommender is None:
        _recommender = NewsRecommender()
    return _recommender

@dataclass
class RecommendedItem:
    title: str
    score: float


@dataclass
class RecommendationResult:
    items: List[RecommendedItem]

def recommend(
    liked_texts: List[str],
    disliked_texts: List[str],
    candidate_news: List[str],
    top_k: Optional[int] = None,
) -> RecommendationResult:

    if not candidate_news:
        raise ValueError("candidate_news cannot be empty")

    rec = get_recommender()

    user_vector: np.ndarray = rec.build_user_vector_from_texts(
        liked_texts=liked_texts,
        disliked_texts=disliked_texts,
    )

    top_indices, scores = rec.rank_candidates(
        user_vector=user_vector,
        candidate_texts=candidate_news,
        top_k=top_k,
    )

    items: List[RecommendedItem] = []
    for idx in top_indices:
        title = candidate_news[idx]
        score = float(scores[idx])
        items.append(RecommendedItem(title=title, score=score))

    return RecommendationResult(items=items)

def self_test() -> bool:
    try:
        _ = recommend(
            liked_texts=["test liked"],
            disliked_texts=["test disliked"],
            candidate_news=["news A", "news B"],
        )
        return True
    except Exception as e:
        print("[model_core.self_test] FAILED:", e)
        return False
