from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from .scraper import fetch_and_parse

app = FastAPI(title="Scrapper (BS4)", version="1.0.0")


class ScrapeRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape")
async def scrape(req: ScrapeRequest):
    try:
        data = await fetch_and_parse(str(req.url))
        return data.__dict__
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
