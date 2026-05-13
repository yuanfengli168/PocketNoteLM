from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(String(16))  # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    session: Mapped["Session"] = relationship("Session", back_populates="messages")


class DocIngestionRecord(Base):
    """Tracks which files have been ingested so we can skip unchanged ones on restart."""
    __tablename__ = "doc_ingestion_records"

    filename: Mapped[str] = mapped_column(String(512), primary_key=True)
    mtime: Mapped[float] = mapped_column(Float)   # os.path.getmtime
    size: Mapped[int] = mapped_column(Integer)    # bytes
    chunks_indexed: Mapped[int] = mapped_column(Integer)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
