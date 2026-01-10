from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from infr.postgres.models import Article


def upsert_article(
    db: Session,
    *,
    url: str,
    title: str,
    content: str | None,
    source: str,
    language: str | None = None,
    published_at: datetime | None = None,
) -> Article:
    a = db.query(Article).filter(Article.url == url).one_or_none()
    if a:
        a.title = title
        a.content = content
        a.source = source
        a.language = language
        a.published_at = published_at or a.published_at
        db.commit()
        db.refresh(a)
        return a

    a = Article(
        url=url,
        title=title,
        content=content,
        source=source,
        language=language,
        published_at=published_at,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def list_latest_articles(db: Session, limit: int = 10, offset: int = 0) -> list[Article]:
    return (
        db.query(Article)
        .order_by(desc(Article.published_at), desc(Article.created_at))
        .offset(offset)
        .limit(limit)
        .all()
    )


def list_candidate_articles(db: Session, limit: int = 50) -> list[Article]:
    return (
        db.query(Article)
        .order_by(desc(Article.published_at), desc(Article.created_at))
        .limit(limit)
        .all()
    )


def get_articles_by_ids(db: Session, ids: list[int]) -> list[Article]:
    if not ids:
        return []
    rows = db.query(Article).filter(Article.id.in_(ids)).all()
    by_id = {a.id: a for a in rows}
    return [by_id[i] for i in ids if i in by_id]
