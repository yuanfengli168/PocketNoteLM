"""
Vizor PS Chatbot — FastAPI backend entry point.

Startup sequence:
1. Init SQLite tables
2. Ingest documents from DOCS_FOLDER_PATH (if any)
3. Start uvicorn server

Endpoints:
  POST /chat          — stream a RAG-powered LLM response
  POST /admin/ingest  — re-index documents
  POST /admin/stop    — gracefully shut down the server
  GET  /health        — liveness check
"""

import logging
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db.database import init_db
from routers.admin import router as admin_router
from routers.chat import router as chat_router
from services.ingest import ingest_documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Vizor PS Chatbot backend…")
    init_db()
    logger.info("Database initialised.")
    try:
        result = ingest_documents()
        logger.info("Document ingestion complete: %s", result)
    except Exception:
        logger.exception("Document ingestion failed — continuing without indexed docs.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Vizor PS Chatbot API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow the frontend origin (update when deploying)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten to specific origins when auth is added
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=1,
    )
