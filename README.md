# Advanced_ai_model — Anime News (Scraper + API + Recommender + Telegram Bot)

A microservice-based project that:
1) pulls anime news from RSS feeds,  
2) enriches items via a scrapper service (extracts article text from URLs),  
3) stores data in PostgreSQL,  
4) exposes data via an API gateway,  
5) generates recommendations using sentence-transformers embeddings,  
6) provides a Telegram bot interface for users.

---

## Services

- **api** (Gateway) — main entrypoint (FastAPI).  
  - Fetches RSS, calls `scrapper` to enrich articles, writes to DB
  - Calls `ai` service for `/recommend`
- **scrapper** — FastAPI service that extracts text/metadata from a given URL (`POST /scrape`)
- **ai** — FastAPI service that serves `/recommend` using embeddings (sentence-transformers)
- **postgres** — PostgreSQL database
- **bot** — Telegram bot that calls the API (e.g. `/news`, `/recommend`)

---

## Architecture (high level)

Telegram Bot -> API Gateway -> Postgres
|
+-> Scrapper (POST /scrape)
|
+-> AI Service (POST /recommend)

---

## Requirements

- Docker + Docker Compose v2
- (Optional) Python 3.11 if you want to run services locally without Docker

---

## Quick start (Docker)

From the repo root:

```bash
docker compose up -d --build
docker compose ps

check /health:

curl -s http://localhost:8000/health
curl -s http://localhost:8003/health
curl -s http://localhost:8002/health
