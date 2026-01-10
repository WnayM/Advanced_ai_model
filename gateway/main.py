from __future__ import annotations

import os
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from shared.logging import setup_logging, get_logger
from gateway.db import get_db
from gateway.news_sources import DEFAULT_RSS_SOURCES
from gateway.fetcher import fetch_rss_items, enrich_with_scrapper

from infr.postgres.repositories import (
    get_or_create_user,
    upsert_article,
    list_latest_articles,
    list_candidate_articles,
    get_articles_by_ids,
    add_event,
    get_user_liked_texts,
    get_user_disliked_texts,
    get_user_rated_article_ids,
)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

setup_logging()
logger = get_logger(__name__)

AI_URL = os.getenv("AI_URL", "http://ai:8002")
SCRAPPER_URL = os.getenv("SCRAPPER_URL", "http://scrapper:8003")
FETCH_INTERVAL_MIN = int(os.getenv("FETCH_INTERVAL_MIN", "30"))

app = FastAPI(title="Gateway API", version="1.0.0")


# ----------------- DTOs -----------------

class HealthResponse(BaseModel):
    status: str


class EnsureUserRequest(BaseModel):
    external_id: str


class EnsureUserResponse(BaseModel):
    user_id: int


class ArticleDTO(BaseModel):
    id: int
    url: str
    title: str
    content: Optional[str] = None
    source: str
    published_at: Optional[str] = None


class ArticlesResponse(BaseModel):
    items: List[ArticleDTO]


class EventRequest(BaseModel):
    external_id: str
    article_id: int
    event_type: str  # "like" | "dislike"


class RecommendRequest(BaseModel):
    external_id: str
    candidate_limit: int = 50
    top_k: int = 5


class RecommendedArticleDTO(BaseModel):
    id: int
    title: str
    url: str
    score: float
    source: str


class RecommendResponse(BaseModel):
    items: List[RecommendedArticleDTO]


# ----------------- Helpers -----------------

def _article_to_dto(a) -> ArticleDTO:
    return ArticleDTO(
        id=a.id,
        url=a.url,
        title=a.title,
        content=a.content,
        source=a.source,
        published_at=a.published_at.isoformat() if a.published_at else None,
    )


async def call_ai_recommend(liked: list[str], disliked: list[str], candidates: list[str], top_k: int) -> list[dict]:
    payload = {
        "liked_texts": liked,
        "disliked_texts": disliked,
        "candidate_news": candidates,
        "top_k": top_k,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(f"{AI_URL}/recommend", json=payload)
        r.raise_for_status()
        data = r.json()
    return data.get("items", [])


# ----------------- API -----------------

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/users/ensure", response_model=EnsureUserResponse)
def ensure_user(req: EnsureUserRequest, db: Session = Depends(get_db)) -> EnsureUserResponse:
    u = get_or_create_user(db, req.external_id)
    return EnsureUserResponse(user_id=int(u.id))


@app.get("/articles/latest", response_model=ArticlesResponse)
def latest_articles(limit: int = 10, offset: int = 0, db: Session = Depends(get_db)) -> ArticlesResponse:
    rows = list_latest_articles(db, limit=limit, offset=offset)
    return ArticlesResponse(items=[_article_to_dto(a) for a in rows])


@app.post("/events", response_model=HealthResponse)
def post_event(req: EventRequest, db: Session = Depends(get_db)) -> HealthResponse:
    if req.event_type not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="event_type must be like|dislike")

    u = get_or_create_user(db, req.external_id)
    _ = add_event(db, user_id=int(u.id), article_id=req.article_id, event_type=req.event_type, event_value=1)
    return HealthResponse(status="ok")


@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest, db: Session = Depends(get_db)) -> RecommendResponse:
    u = get_or_create_user(db, req.external_id)

    liked = get_user_liked_texts(db, int(u.id), limit=30)
    disliked = get_user_disliked_texts(db, int(u.id), limit=30)

    if len(liked) < 1:
        raise HTTPException(status_code=400, detail="Need at least 1 liked article to recommend.")

    rated_ids = get_user_rated_article_ids(db, int(u.id))

    candidates_rows = list_candidate_articles(db, limit=req.candidate_limit)
    # фильтруем те, что уже оценены
    candidates_rows = [a for a in candidates_rows if a.id not in rated_ids]

    if not candidates_rows:
        raise HTTPException(status_code=400, detail="No candidates to recommend.")

    candidate_texts = [(a.title or "") + "\n" + (a.content or "") for a in candidates_rows]

    try:
        ai_items = await call_ai_recommend(liked, disliked, candidate_texts, top_k=req.top_k)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    # ai_items: [{"index": i, "score": s}, ...] индексы относительно candidates_rows
    rec_ids: list[int] = []
    scores_by_article_id: dict[int, float] = {}

    for it in ai_items:
        idx = int(it["index"])
        score = float(it["score"])
        if 0 <= idx < len(candidates_rows):
            art_id = int(candidates_rows[idx].id)
            rec_ids.append(art_id)
            scores_by_article_id[art_id] = score

    articles = get_articles_by_ids(db, rec_ids)

    out: list[RecommendedArticleDTO] = []
    for a in articles:
        out.append(
            RecommendedArticleDTO(
                id=int(a.id),
                title=a.title,
                url=a.url,
                score=float(scores_by_article_id.get(int(a.id), 0.0)),
                source=a.source,
            )
        )
    return RecommendResponse(items=out)


# ----------------- Scheduler: RSS -> Scrapper -> DB -----------------

async def _job_fetch_news():
    logger.info("Scheduler: fetching news")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # прогрев scrapper health (не обязательно)
        try:
            await client.get(f"{SCRAPPER_URL}/health")
        except Exception:
            pass

    from infr.postgres.db import SessionLocal
    db = SessionLocal()
    try:
        for src in DEFAULT_RSS_SOURCES:
            src_name = src["name"]
            rss = src["rss"]
            items = await fetch_rss_items(rss, src_name, limit=20)

            for it in items:
                # enrich content через scrapper
                enriched = await enrich_with_scrapper(SCRAPPER_URL, it.url)
                content = enriched or it.content

                upsert_article(
                    db,
                    url=it.url,
                    title=it.title,
                    content=content,
                    source=it.source,
                    language="en",
                    published_at=it.published_at,
                )

        logger.info("Scheduler: done")
    finally:
        db.close()


scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def on_startup():
    # создать таблицы (быстро и грязно). лучше потом заменить на alembic.
    from infr.postgres.db import engine
    from infr.postgres.db import Base
    Base.metadata.create_all(bind=engine)

    scheduler.add_job(_job_fetch_news, "interval", minutes=FETCH_INTERVAL_MIN, id="fetch_news", replace_existing=True)
    scheduler.start()

    # один раз при старте
    try:
        await _job_fetch_news()
    except Exception:
        logger.exception("Initial fetch failed")
