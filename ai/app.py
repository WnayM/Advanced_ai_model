from __future__ import annotations

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from shared.logging import setup_logging, get_logger
from ai.model_core import (
    recommend as core_recommend,
    self_test as core_self_test,
    RecommendationResult,
)

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="Anime News Recommender API",
    version="1.0.0",
    description="Recommender based on sentence-transformers embeddings",
)


class RecommendRequest(BaseModel):
    liked_texts: List[str]
    disliked_texts: List[str] = []
    candidate_news: List[str]
    top_k: Optional[int] = None


class RecommendedItemDTO(BaseModel):
    index: int
    score: float


class RecommendResponse(BaseModel):
    items: List[RecommendedItemDTO]


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    ok = core_self_test()
    if ok:
        return HealthResponse(status="ok")
    raise HTTPException(status_code=500, detail="Model self-test failed")


@app.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(payload: RecommendRequest) -> RecommendResponse:
    logger.info(
        "POST /recommend called",
        extra={
            "liked_count": len(payload.liked_texts),
            "disliked_count": len(payload.disliked_texts),
            "candidates_count": len(payload.candidate_news),
            "top_k": payload.top_k,
        },
    )

    try:
        result: RecommendationResult = core_recommend(
            liked_texts=payload.liked_texts,
            disliked_texts=payload.disliked_texts,
            candidate_news=payload.candidate_news,
            top_k=payload.top_k,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Internal model error")
        raise HTTPException(status_code=500, detail=f"Internal model error: {e}")

    items_dto = [RecommendedItemDTO(index=i.index, score=i.score) for i in result.items]
    return RecommendResponse(items=items_dto)
