# PocketNoteLM

A free, open source, privacy-first [NotebookLM](https://notebooklm.google.com) alternative that runs entirely on your machine.

Drop in your PDFs, notes, or documents and ask questions in plain English. All processing happens locally via [Ollama](https://ollama.com) — no cloud, no API keys, no data leaving your machine.

Built for **macOS Apple Silicon**.

---

## Features

- **Local-first RAG** — Retrieval-Augmented Generation over your own documents
- **100% private** — Everything runs locally via Ollama; no data sent to external services
- **Streaming responses** — Real-time token streaming via Server-Sent Events
- **Multi-turn chat** — Persistent conversation history across sessions
- **OCR support** — Extracts text from image-embedded PDFs (e.g. scanned pages, screenshots)
- **Smart re-ingestion** — Only re-indexes documents when files actually change
- **Multi-format** — PDFs, Word docs, and more

---

## Hardware Requirements

| RAM | Recommended model |
|-----|------------------|
| 32 GB | `qwen3:14b` |
| 64 GB | `qwen3:32b` |

Embeddings use `nomic-embed-text` (768-dim, fast on Apple Silicon).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python 3.13 + FastAPI |
| LLM | Ollama (any local model) |
| Vector Store | ChromaDB (local) |
| Database | SQLite |
| OCR | pymupdf + pytesseract |

---

## Getting Started

### Prerequisites

- macOS with Apple Silicon (M1 or later recommended)
- [Ollama](https://ollama.com) installed
- Python 3.12+
- Node.js 18+
- Tesseract (for OCR): `brew install tesseract`

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PocketNoteLM.git
cd PocketNoteLM

# Pull the models
ollama pull qwen3:14b          # or qwen3:32b for 64 GB+ machines
ollama pull nomic-embed-text

# Backend setup
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set DOCS_FOLDER_PATH to your documents folder

# Frontend setup
cd ../frontend
npm install
npm run build
```

### Running

```bash
# Terminal 1 — backend
cd backend && python main.py

# Terminal 2 — frontend
cd frontend && npm run preview
```

Open [http://localhost:4173](http://localhost:4173).

### Environment Variables

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen3:14b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
DOCS_FOLDER_PATH=/path/to/your/documents
ADMIN_TOKEN=change-me-to-a-strong-secret
```

---

## Project Structure

```
PocketNoteLM/
├── frontend/           # React UI
├── backend/            # FastAPI service
│   ├── main.py         # App entrypoint
│   ├── config.py       # Settings from .env
│   ├── db/             # SQLite models
│   ├── routers/        # API endpoints
│   └── services/       # RAG, ingestion, cache
├── launchd/            # macOS auto-start configs
├── design.md           # Architecture document
└── TimeLine.md         # Roadmap
```

---

## Auto-start on Boot (macOS)

See [backend/README.md](backend/README.md) for launchd setup instructions.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

MIT
