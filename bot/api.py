from __future__ import annotations
import httpx
from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:
    id: int
    url: str
    title: str
    content: Optional[str]
    source: str
    published_at: Optional[str]


class GatewayClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def ensure_user(self, external_id: str) -> int:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(f"{self.base_url}/users/ensure", json={"external_id": external_id})
            r.raise_for_status()
            return int(r.json()["user_id"])

    async def latest_articles(self, limit: int = 10, offset: int = 0) -> list[Article]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(f"{self.base_url}/articles/latest", params={"limit": limit, "offset": offset})
            r.raise_for_status()
            data = r.json()["items"]
            return [Article(**x) for x in data]

    async def event(self, external_id: str, article_id: int, event_type: str) -> None:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(f"{self.base_url}/events", json={
                "external_id": external_id,
                "article_id": article_id,
                "event_type": event_type
            })
            r.raise_for_status()

    async def recommend(self, external_id: str, top_k: int = 5) -> list[dict]:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self.base_url}/recommend", json={
                "external_id": external_id,
                "top_k": top_k,
                "candidate_limit": 50
            })
            r.raise_for_status()
            return r.json()["items"]
