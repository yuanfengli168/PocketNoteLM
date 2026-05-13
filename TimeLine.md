# Project Timeline

## Vision

A free, open source, privacy-first alternative to Google NotebookLM — runs 100% locally on Apple Silicon Macs. Feed it your PDFs, Word docs, screenshots, and team chat history; ask questions in plain text; get answers grounded in your actual documentation.

**Target hardware:** macOS with Apple Silicon, minimum M1 with 32GB unified memory.

| RAM | Recommended model |
|---|---|
| 32 GB (M1/M2/M3/M4) | `qwen3:14b` |
| 64 GB (M2/M3 Max) | `qwen3:32b` |
| 128 GB (M2/M3/M4 Ultra, M5 Max) | future 70b+ models |

---

## Phase 1 — Open Source Launch (target: EOD Saturday 17 May 2026)

- [ ] Clean up README with full setup instructions
- [ ] Write a one-command install script (`install.sh`): Homebrew → Ollama → pull `qwen3:14b` → start services
- [ ] Scrub `.env` and any internal content from repo history
- [ ] Add `CONTRIBUTING.md` with how to add new doc sources
- [ ] Publish repo publicly on GitHub

**What ships:** working RAG chatbot, PDF + DOCX + OCR image ingestion, local Ollama LLM, React frontend, FastAPI backend, auto-start via launchd, skip re-ingestion on unchanged files.

---

## Phase 2 — Quality & Usability (weeks after launch)

- [ ] **Source citations in the chat UI** — show `[Source: filename, page N]` as inline references in each answer bubble
- [ ] **PNG direct upload support** — OCR standalone images, same pipeline as PDF-embedded images
- [ ] **Upload UI** — drag-and-drop files in the frontend → POST to `/admin/ingest` (removes the manual folder-drop requirement)
- [ ] **Parent Document Retriever** — embed at 256 chars for precise matching, retrieve 1024-char parent chunk for LLM context (fixes chunk boundary fragmentation)
- [ ] **Switch to `mxbai-embed-large`** — higher quality embeddings for technical text, still free/local

---

## Phase 3 — Power Features (after Phase 2 stable)

- [ ] **Teams / Slack chat export ingestion** — parse JSON exports, treat each thread as a document; unique differentiator vs NotebookLM
- [ ] **Per-user notebooks** — each user maintains their own separate doc corpus
- [ ] **Install script UX** — "open Terminal once, then never again": launchd auto-start, menubar status indicator

---

## Phase 4 — Native App (if community traction)

- [ ] Wrap in **Tauri** for a proper `.dmg` installer with menubar icon and auto-update
- [ ] App Store distribution (requires notarisation + Apple Developer account)

---

## Architecture Notes

- Ollama must be installed separately — models are too large to bundle in a `.dmg`
- The competitive position: "NotebookLM but open source, private, runs on your Mac"
- Trust is the core value prop — sensitive work docs never leave the machine
