🧠 Advanced AI Model — Anime News Recommender

A microservice for generating personalized anime-related news recommendations using text embeddings.
The system is built on FastAPI and powered by SentenceTransformers for vector-based semantic similarity.

At the current stage, the project includes:

an embedding model wrapper (EmbeddingModel);

a recommendation pipeline (NewsRecommender);

a production-ready HTTP API (/health, /recommend);

centralized structured logging (shared.logging).

🚀 Tech Stack

Python 3.11

FastAPI — REST API framework

SentenceTransformers — embeddings
Default model: sentence-transformers/all-MiniLM-L6-v2

NumPy — vector operations

Pydantic — request/response schemas

Structured logging — via Python logging + dictConfig
