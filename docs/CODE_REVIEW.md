# PocketNoteLM — Code Review

> Reviewed: May 13, 2026

## Project Summary

**PocketNoteLM** is a privacy-first, local-running RAG (Retrieval-Augmented Generation) chatbot for macOS Apple Silicon. Users upload PDFs and Word documents, then ask questions about them using local LLM inference via Ollama and vector similarity search via ChromaDB.

**Stack:**
- **Frontend**: React 18 + TypeScript + Vite
- **Backend**: Python 3.13 + FastAPI with async SSE streaming
- **LLM**: Ollama (e.g. `qwen3:14b` / `qwen3:32b`)
- **Vector Store**: ChromaDB (local, persisted)
- **Database**: SQLite for chat history
- **OCR**: PyMuPDF + Tesseract for embedded images in PDFs

---

## 🔴 Critical Security Issues

### 1. Admin Token Exposed in Frontend Bundle
**File**: `frontend/src/utils/api.ts` (line 4)  
**OWASP**: A02:2021 — Broken Authentication

`VITE_ADMIN_TOKEN` is embedded in the Vite build and compiled into the production JS bundle. This means:
- The token is visible in browser DevTools (network tab and JS source)
- Any user with frontend access can call `/admin/stop` to shut down the backend

**Fix**: Remove `VITE_ADMIN_TOKEN` from the frontend entirely. The admin shutdown should be triggered via a backend-only mechanism (e.g. a password confirmation that the backend validates, without exposing the actual token to the client).

---

### 2. CORS Configured to Allow All Origins
**File**: `backend/main.py` (lines 58–64)  
**OWASP**: A01:2021 — Broken Access Control

```python
allow_origins=["*"],
```

Any malicious website can make requests to the backend.

**Fix**: Restrict to `http://localhost:4172` for local deployment.

---

## 🟡 Medium Issues

### 3. `slowapi` Installed but Never Used
**File**: `backend/requirements.txt` (line 17)

`slowapi` is listed as a dependency but no rate limiting middleware or decorators are applied anywhere in the codebase. Without rate limiting, the backend is open to resource exhaustion from runaway requests or LLM inference flooding.

**Fix**: Either implement `@limiter.limit()` decorators on endpoints, or remove `slowapi` from dependencies.

---

### 4. Weak Default Admin Token
**File**: `backend/config.py` (line 24)

```python
admin_token: str = "change-me"
```

**Fix**: Auto-generate a random UUID as the default, or refuse to start if the token hasn't been changed from the default.

---

### 5. No Input Validation on Chat Messages
**File**: `backend/routers/chat.py` (lines 25–28)

```python
class ChatRequest(BaseModel):
    session_id: str
    message: str        # No max length
    history: list[dict[str, str]] = []
```

A user could send an extremely large `message` or `session_id`, causing memory or database issues.

**Fix**:
- Add `Field(max_length=10000)` to `message`
- Validate `session_id` is a UUID format

---

### 6. App Name Mismatch (Stale Copy-Paste)
**File**: `backend/main.py` (line 1–3)

The app is titled `"Vizor PS Chatbot"` — leftover from a previous project. All other files correctly use `"PocketNoteLM"`.

**Fix**: Update the app title in `main.py`.

---

### 7. Inconsistent Document Ingestion Return Schema
**File**: `backend/services/ingest.py` (lines 137, 150)

Skipped runs return `{"skipped": True, ...}` but normal runs omit the `"skipped"` key entirely. Callers expecting a consistent schema may break.

**Fix**: Always include `"skipped": bool` in the return value.

---

### 8. No Validation of `DOCS_FOLDER_PATH`
**File**: `backend/services/ingest.py` (lines 117–120)

If the docs folder doesn't exist, a warning is logged but the backend continues silently. Users may not notice that no documents are indexed.

**Fix**: Raise an error on startup or clearly surface this state in a `/health` endpoint.

---

### 9. No Handling of ChromaDB Initialization Failures
**File**: `backend/services/rag.py` (lines 115–121)

If ChromaDB fails to initialize (corrupt DB, permission error, missing deps), the error bubbles up uncaught.

**Fix**: Wrap in `try/except` with a meaningful error message.

---

### 10. Frontend Doesn't Validate API Response Format
**File**: `frontend/src/utils/api.ts` (lines 38–46)

Malformed SSE lines from the backend are silently skipped with no logging.

**Fix**: Log a warning for unexpected SSE formats.

---

### 11. `design.md` References OpenAI Instead of Ollama
**File**: `design.md` (lines 48–51)

The design doc still mentions OpenAI `gpt-4o` as the MVP model, contradicting the Ollama-only implementation in `config.py` and the README.

**Fix**: Update `design.md` to reflect the current Ollama-based architecture.

---

### 12. launchd Plist Requires Manual Path Updates
**File**: `launchd/com.pocketnotelm.backend.plist`

Contains a placeholder path:
```xml
<string>/Users/REPLACE_WITH_YOUR_USERNAME/pocketnotelm-start-backend.sh</string>
```

`install.sh` patches this, but if the script fails mid-way, the service breaks silently.

**Fix**: Add validation in `install.sh` to confirm the substitution succeeded.

---

## 📋 Missing / Incomplete Features

| Feature | Priority (per design.md) | Notes |
|---|---|---|
| Rate limiting | High | `slowapi` is installed but not wired up |
| User authentication (JWT) | High | No login system exists |
| Document management UI | Medium | No way to view, delete, or re-index individual files |
| Feedback buttons (👍/👎) | High | Mentioned in design.md, not implemented |
| Test suite | — | No `tests/` directory exists |
| Chat history pagination | — | All history loaded at once; could be memory-intensive |

---

## ✅ What's Done Well

- Proper `async`/`await` and SSE streaming patterns in FastAPI
- SQLAlchemy ORM used correctly — no raw SQL injection risk
- Dependency injection via FastAPI `Depends()`
- ChromaDB hash-based deduplication to avoid redundant indexing
- Lost-in-middle mitigation in RAG retrieval (`_reorder_for_lost_in_middle`)
- Proper SSE framing for token streaming on the frontend

---

## OWASP Top 10 Summary

| OWASP Category | Issue | Severity | Location |
|---|---|---|---|
| A01: Broken Access Control | CORS `allow_origins=["*"]` | 🔴 Critical | `backend/main.py` |
| A01: Broken Access Control | Admin token on frontend | 🔴 Critical | `frontend/src/utils/api.ts` |
| A02: Broken Authentication | Weak default admin token | 🟡 Medium | `backend/config.py` |
| A04: Insecure Design | No rate limiting | 🟡 Medium | `backend/requirements.txt` |
| A07: Auth Failures | No input validation on messages | 🟡 Medium | `backend/routers/chat.py` |

---

## Recommended Priority Order

1. **Remove `VITE_ADMIN_TOKEN` from frontend** — most urgent security fix
2. **Restrict CORS origins** — quick config change
3. **Add input validation** (`message`, `session_id`) — prevents abuse
4. **Implement or remove `slowapi`** — either wire it up or drop it
5. **Fix weak default admin token** — generate UUID or enforce change
6. **Add test suite** — no tests currently exist
7. **Update `design.md`** to match current architecture
