#!/bin/zsh
# PocketNoteLM — one-command setup for macOS Apple Silicon
# Usage: zsh install.sh

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log()  { echo "${GREEN}[install]${NC} $*"; }
warn() { echo "${YELLOW}[warn]${NC}   $*"; }
fail() { echo "${RED}[error]${NC}  $*" >&2; exit 1; }

# ── 1. Check architecture ─────────────────────────────────────────────────────
if [[ "$(uname -m)" != "arm64" ]]; then
  warn "This tool is optimised for Apple Silicon (arm64). Detected: $(uname -m)"
  warn "It may still work, but performance will be degraded."
fi

# ── 2. Homebrew ───────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
  log "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  log "Homebrew already installed."
fi

# ── 3. System dependencies ────────────────────────────────────────────────────
log "Installing system dependencies (tesseract, node)..."
brew install tesseract node 2>/dev/null || true

# ── 4. Ollama ─────────────────────────────────────────────────────────────────
if ! command -v ollama &>/dev/null; then
  log "Installing Ollama..."
  brew install ollama
else
  log "Ollama already installed."
fi

# Start Ollama in background if not running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
  log "Starting Ollama server..."
  ollama serve &>/tmp/ollama.log &
  sleep 3
fi

# ── 5. Pull models ────────────────────────────────────────────────────────────
RAM_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
log "Detected ${RAM_GB} GB RAM."

if (( RAM_GB >= 60 )); then
  LLM_MODEL="qwen3:32b"
  warn "64 GB+ detected — pulling qwen3:32b (~20 GB). This will take a while."
else
  LLM_MODEL="qwen3:14b"
  log "Pulling qwen3:14b (~9 GB)..."
fi

ollama pull "$LLM_MODEL"
ollama pull nomic-embed-text

log "Models ready: $LLM_MODEL + nomic-embed-text"

# ── 6. Backend Python setup ───────────────────────────────────────────────────
log "Setting up backend..."
cd "$REPO_DIR/backend"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  # Patch the model to match what we pulled
  sed -i '' "s|^OLLAMA_MODEL=.*|OLLAMA_MODEL=${LLM_MODEL}|" .env
  log ".env created from .env.example with OLLAMA_MODEL=${LLM_MODEL}."
  warn "Edit backend/.env — set DOCS_FOLDER_PATH to your documents folder."
else
  log "backend/.env already exists, skipping."
fi

# ── 7. Frontend setup ─────────────────────────────────────────────────────────
log "Setting up frontend..."
cd "$REPO_DIR/frontend"
npm install --silent

if [[ ! -f .env ]]; then
  cp .env.example .env
  log "frontend/.env created."
fi

npm run build --silent
log "Frontend built."

# ── 8. launchd auto-start (optional) ─────────────────────────────────────────
echo ""
read "AUTOSTART?Set up auto-start on login via launchd? [y/N] "
if [[ "$AUTOSTART" =~ ^[Yy]$ ]]; then
  # Backend
  cp "$REPO_DIR/launchd/start-backend.sh" ~/pocketnotelm-start-backend.sh
  sed -i '' "s|REPO_DIR=\"\$HOME/PocketNoteLM\"|REPO_DIR=\"${REPO_DIR}\"|" ~/pocketnotelm-start-backend.sh
  chmod +x ~/pocketnotelm-start-backend.sh

  cp "$REPO_DIR/launchd/com.pocketnotelm.backend.plist" ~/Library/LaunchAgents/
  sed -i '' "s|REPLACE_WITH_YOUR_USERNAME|$(whoami)|g" ~/Library/LaunchAgents/com.pocketnotelm.backend.plist
  sed -i '' "s|pocketnotelm-start-backend.sh|$(echo ~/pocketnotelm-start-backend.sh)|g" ~/Library/LaunchAgents/com.pocketnotelm.backend.plist
  launchctl load ~/Library/LaunchAgents/com.pocketnotelm.backend.plist

  # Frontend
  cp "$REPO_DIR/launchd/start-frontend.sh" ~/pocketnotelm-start-frontend.sh
  sed -i '' "s|REPO_DIR=\"\$HOME/PocketNoteLM\"|REPO_DIR=\"${REPO_DIR}\"|" ~/pocketnotelm-start-frontend.sh
  chmod +x ~/pocketnotelm-start-frontend.sh

  cp "$REPO_DIR/launchd/com.pocketnotelm.frontend.plist" ~/Library/LaunchAgents/
  sed -i '' "s|REPLACE_WITH_YOUR_USERNAME|$(whoami)|g" ~/Library/LaunchAgents/com.pocketnotelm.frontend.plist
  sed -i '' "s|pocketnotelm-start-frontend.sh|$(echo ~/pocketnotelm-start-frontend.sh)|g" ~/Library/LaunchAgents/com.pocketnotelm.frontend.plist
  launchctl load ~/Library/LaunchAgents/com.pocketnotelm.frontend.plist

  log "Auto-start registered. Backend and frontend will start on next login."
  log "Logs: /tmp/pocketnotelm-backend.log  /tmp/pocketnotelm-frontend.log"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
log "Setup complete!"
echo ""
echo "  1. Edit backend/.env — set DOCS_FOLDER_PATH to your documents folder"
echo "  2. Start the backend:  cd backend && source .venv/bin/activate && python main.py"
echo "  3. Start the frontend: cd frontend && npm run preview"
echo "  4. Open http://localhost:4172"
echo ""
