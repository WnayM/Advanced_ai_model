from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import feedparser
import httpx

from shared.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FetchedItem:
    url: str
    title: str
    source: str
    published_at: Optional[datetime]
    content: Optional[str]


def _parse_dt(entry) -> Optional[datetime]:
    # feedparser может дать published_parsed/updated_parsed
    for key in ("published_parsed", "updated_parsed"):
        v = getattr(entry, key, None)
        if v:
            try:
                return datetime(*v[:6])
            except Exception:
                return None
    return None


async def fetch_rss_items(rss_url: str, source_name: str, limit: int = 20) -> list[FetchedItem]:
    logger.info("Fetching RSS", extra={"rss": rss_url, "source": source_name})
    d = feedparser.parse(rss_url)

    items: list[FetchedItem] = []
    for e in d.entries[:limit]:
        link = getattr(e, "link", None)
        title = getattr(e, "title", None)
        if not link or not title:
            continue

        published_at = _parse_dt(e)

        # summary бывает HTML — оставим как есть, позже scrapper может дать meta description
        summary = getattr(e, "summary", None)

        items.append(
            FetchedItem(
                url=str(link),
                title=str(title),
                source=source_name,
                published_at=published_at,
                content=str(summary) if summary else None,
            )
        )

    return items


async def enrich_with_scrapper(scrapper_url: str, url: str) -> str | None:
    # дергаем твой scrapper: POST /scrape {url}
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(f"{scrapper_url}/scrape", json={"url": url})
            r.raise_for_status()
            data = r.json()
        # берём description, если есть
        desc = data.get("description") or data.get("h1") or data.get("title")
        if desc:
            return str(desc)
    except Exception:
        logger.exception("Scrapper enrich failed", extra={"url": url})
    return None
