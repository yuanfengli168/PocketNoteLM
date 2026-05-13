# Implementation Log

## May 13 2026 — Fixed critical & medium issues from CODE_REVIEW.md

### Critical

- **Removed admin token from frontend bundle** (`frontend/src/utils/api.ts`, `frontend/src/components/Header.tsx`): Deleted `VITE_ADMIN_TOKEN` env var usage; `stopService()` now takes a `token` param; `Header.tsx` prompts the user to type the token at click-time instead of embedding it in the bundle.

- **Restricted CORS origins** (`backend/main.py`): Changed `allow_origins=["*"]` to `["http://localhost:4173", "http://localhost:5173"]`.

### Medium

- **Fixed app name mismatch** (`backend/main.py`): Replaced stale "Vizor PS Chatbot" with "PocketNoteLM" in docstring, startup log, and FastAPI title.

- **Replaced weak default admin token** (`backend/config.py`): Default changed from `"change-me"` to `secrets.token_hex(32)` (auto-generated per process). Token is logged on startup; pin it permanently by setting `ADMIN_TOKEN` in `backend/.env`.

- **Added input validation to chat endpoint** (`backend/routers/chat.py`): `message` capped at `max_length=10_000`; `session_id` validated as UUID format via `@field_validator`.

- **Removed unused `slowapi` dependency** (`backend/requirements.txt`): Was listed but never implemented anywhere in the codebase.

- **Consistent ingest return schema** (`backend/services/ingest.py`): All return paths now include `"skipped": bool` key.

- **ChromaDB init error handling** (`backend/services/rag.py`): Wrapped `Chroma(...)` in try/except; raises `RuntimeError` with a descriptive message instead of a bare crash.

- **Frontend SSE unexpected-line logging** (`frontend/src/utils/api.ts`): Non-`data:` lines in the SSE stream now emit `console.warn` instead of being silently ignored.
