"""
Admin router.

POST /admin/ingest  — re-index documents from DOCS_FOLDER_PATH
POST /admin/stop    — gracefully shut down the server

Both endpoints require a Bearer token matching ADMIN_TOKEN in .env.
"""

import logging
import os
import signal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import get_settings
from services.ingest import ingest_documents

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin")

_bearer = HTTPBearer()


def _verify_token(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> None:
    settings = get_settings()
    if credentials.credentials != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")


@router.post("/ingest", dependencies=[Depends(_verify_token)])
async def ingest():
    """Trigger a full re-ingestion of documents from the configured folder."""
    result = ingest_documents()
    return {"status": "ok", **result}


@router.post("/stop", dependencies=[Depends(_verify_token)])
async def stop():
    """Gracefully shut down the uvicorn server process."""
    logger.info("Stop requested via /admin/stop — sending SIGTERM")
    os.kill(os.getpid(), signal.SIGTERM)
    return {"message": "Server is shutting down."}
