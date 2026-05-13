# PocketNoteLM — Design Document

**Version:** 0.1 | **Date:** 2026-05-09

---

## 1. Overview

Local AI assistant that answers questions by searching user-provided documents (PDFs, Word docs) via RAG, then generating a response using a local LLM. No login for MVP; designed to add auth and more features incrementally.

**Constraints:** Single-user local deployment, backend runs on macOS Apple Silicon, frontend served locally.

---

## 2. Architecture

```
[React UI on GitHub Pages]
        │  HTTPS (REST + SSE streaming)
        ▼
[FastAPI Backend — localhost / ngrok tunnel]
        │
        ├── [LangChain RAG Pipeline]
        │       ├── ChromaDB (vector store, local)
        │       └── LLM Provider (swappable via config)
        │
        ├── [SQLite] — chat history, session metadata
        │
        └── [In-memory cache] — frequent Q&A pairs
```

---

## 3. Frontend (React + Vite → GitHub Pages)

- ChatGPT-style UI: message thread, streaming response, markdown rendering
- No login for MVP; session identified by browser `localStorage` UUID
- **Stop Service button** — calls `POST /admin/stop` on the backend (protected by a simple secret token in `.env`)
- **Auto-deploy:** GitHub Actions workflow on push to `main` → `gh-pages` branch

**Scalability path:** Add auth (JWT / OAuth2), user history, role-based views.

---

## 4. Backend (Python + FastAPI)

- **Async FastAPI** with SSE streaming for real-time token output
- **LangChain** as the orchestration layer — LLM provider is a config switch:
  - MVP: OpenAI `gpt-4o` (text + image support)
  - Future: local Ollama (`qwen3-14b` or similar) via same interface
- **Concurrency:** `uvicorn` with 4 async workers handles 10 simultaneous users comfortably
- **Caching:** Python `cachetools` TTL cache for repeated questions (exact-match hash key); upgrade to Redis if needed
- **Rate limiting:** `slowapi` middleware to prevent abuse
- **Auto-start on laptop boot:** macOS `launchd` plist registers the service; a shell wrapper handles venv activation and port binding

---

## 5. Data Layer

| Store | Technology | Purpose |
|-------|-----------|---------|
| Vector store | ChromaDB (local) | Document embeddings + semantic search |
| Relational | SQLite | Chat history, session records |
| Cache | `cachetools` in-process | Frequent Q&A deduplication |
| Config / secrets | `.env` file | API keys, doc folder path, admin token |

**Upgrade path:** ChromaDB → Qdrant (Docker), SQLite → PostgreSQL, in-process cache → Redis — all are drop-in swaps via LangChain / SQLAlchemy abstractions.

---

## 6. Document Ingestion Module

- Folder path stored in `.env` as `DOCS_FOLDER_PATH`
- Supported formats: PDF (`pypdf`), Word (`python-docx`), images (via LLM vision)
- **Pipeline:** Load → chunk (512 tokens, 50-token overlap) → embed (`text-embedding-3-small`) → upsert ChromaDB
- **Trigger:** Run on backend startup + expose `POST /admin/ingest` endpoint to re-index on demand
- Images inside documents are extracted and described by the LLM (multimodal), then stored as text chunks

---

## 7. Deployment

### Frontend
- `main` branch push → GitHub Actions → `vite build` → deploy to `gh-pages`
- Environment variable `VITE_API_URL` points to backend URL (ngrok or static IP)

### Backend (macOS laptop)
- `launchd` plist at `~/Library/LaunchAgents/com.pocketnotelm.backend.plist`
- Service starts on login, restarts on crash
- **Stop endpoint:** `POST /admin/stop` (bearer token auth) shuts down uvicorn gracefully; frontend exposes this as a button
- Exposed via **ngrok** (free tier) or local network IP for team access

---

## 8. Recommended Next Steps (MVP 1.0 → 1.x)

| Priority | Feature |
|----------|---------|
| High | Add user login (JWT + simple user table) |
| High | Feedback buttons (👍/👎) to flag bad answers |
| Medium | Nightly re-ingestion cron job for updated docs |
| Medium | Source citation — show which doc/chunk the answer came from |
| Low | Switch to local Ollama model for offline/private use |
| Low | Multilingual support for non-English docs |

---

## 9. Tech Stack Summary

| Layer | Choice |
|-------|--------|
| Frontend | React + Vite + TypeScript |
| Frontend hosting | GitHub Pages (via GitHub Actions) |
| Backend | Python 3.12 + FastAPI + LangChain |
| LLM (MVP) | OpenAI `gpt-4o` |
| LLM (future) | Ollama (`qwen3-14b`) |
| Vector DB | ChromaDB → Qdrant |
| Relational DB | SQLite → PostgreSQL |
| Cache | `cachetools` → Redis |
| Backend hosting | macOS laptop via `launchd` + ngrok |
