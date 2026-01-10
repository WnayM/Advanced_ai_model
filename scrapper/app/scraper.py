from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx
from bs4 import BeautifulSoup


@dataclass
class PageData:
    url: str
    title: Optional[str]
    h1: Optional[str]
    description: Optional[str]


async def fetch_and_parse(url: str, timeout_s: float = 15.0) -> PageData:
    headers = {"User-Agent": "lame-cow-scrapper/1.0"}

    async with httpx.AsyncClient(headers=headers, timeout=timeout_s, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    title = soup.title.get_text(strip=True) if soup.title else None
    h1_tag = soup.find("h1")
    h1 = h1_tag.get_text(strip=True) if h1_tag else None

    desc = None
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"].strip()

    return PageData(url=url, title=title, h1=h1, description=desc)
