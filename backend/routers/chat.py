"""
Chat router — POST /chat

Streams the LLM response back to the client as Server-Sent Events (SSE).
Each token is sent as:  data: <token>\n\n
End of stream is signalled with:  data: [DONE]\n\n
"""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from db.database import get_db
from db.models import Message, Session
from services.cache import get_cached_answer, set_cached_answer
from services.rag import answer_with_rag

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: list[dict[str, str]] = []


async def _stream_response(request: ChatRequest, db: DBSession):
    """Generator that streams SSE tokens and persists the conversation."""
    question = request.message.strip()
    session_id = request.session_id

    # Ensure session row exists
    session = db.get(Session, session_id)
    if not session:
        session = Session(id=session_id)
        db.add(session)
        db.commit()

    # Persist user message
    db.add(Message(session_id=session_id, role="user", content=question))
    db.commit()

    # Check cache first
    cached = get_cached_answer(question, session_id)
    if cached:
        logger.info("Cache hit for session %s", session_id)
        # Stream cached answer token-by-token to keep SSE framing valid
        # (a single yield with \n\n inside would break SSE event boundaries)
        for token in cached:
            if token == "\n":
                yield "data: \n\n"
            else:
                yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
        db.add(Message(session_id=session_id, role="assistant", content=cached))
        db.commit()
        return

    # Stream from RAG pipeline
    full_answer: list[str] = []
    async for token in answer_with_rag(question, request.history):
        full_answer.append(token)
        yield f"data: {token}\n\n"

    yield "data: [DONE]\n\n"

    # Persist assistant reply + cache it
    answer_text = "".join(full_answer)
    db.add(Message(session_id=session_id, role="assistant", content=answer_text))
    db.commit()
    set_cached_answer(question, session_id, answer_text)


@router.post("/chat")
async def chat(request: ChatRequest, db: DBSession = Depends(get_db)):
    return StreamingResponse(
        _stream_response(request, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
