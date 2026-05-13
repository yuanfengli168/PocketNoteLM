#!/bin/zsh
# Startup wrapper for launchd — activates the venv before running the backend
# NOTE: install.sh configures REPO_DIR automatically. Edit it here if needed.

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

REPO_DIR="$HOME/PocketNoteLM"

cd "$REPO_DIR/backend"
source .venv/bin/activate
exec python main.py
