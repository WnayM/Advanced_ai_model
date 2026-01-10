from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import desc
from infr.postgres.models import UserEvent, Article


def add_event(db: Session, *, user_id: int, article_id: int, event_type: str, event_value: int = 1) -> UserEvent:
    ev = UserEvent(
        user_id=user_id,
        article_id=article_id,
        event_type=event_type,
        event_value=event_value,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def get_user_rated_article_ids(db: Session, user_id: int) -> set[int]:
    rows = db.query(UserEvent.article_id).filter(UserEvent.user_id == user_id).all()
    return {r[0] for r in rows}


def _join_event_articles(db: Session, user_id: int, event_type: str, limit: int = 30) -> list[str]:
    q = (
        db.query(Article.title, Article.content)
        .join(UserEvent, UserEvent.article_id == Article.id)
        .filter(UserEvent.user_id == user_id, UserEvent.event_type == event_type)
        .order_by(desc(UserEvent.event_ts))
        .limit(limit)
    )
    texts: list[str] = []
    for title, content in q.all():
        t = title or ""
        c = content or ""
        texts.append(f"{t}\n{c}".strip())
    return texts


def get_user_liked_texts(db: Session, user_id: int, limit: int = 30) -> list[str]:
    return _join_event_articles(db, user_id, "like", limit)


def get_user_disliked_texts(db: Session, user_id: int, limit: int = 30) -> list[str]:
    return _join_event_articles(db, user_id, "dislike", limit)
