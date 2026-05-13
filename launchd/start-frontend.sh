#!/bin/zsh
# Wrapper script for launchd — sets up nvm environment before starting the frontend
# NOTE: install.sh configures REPO_DIR automatically. Edit it here if needed.

export NVM_DIR="$HOME/.nvm"
# Load nvm
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

REPO_DIR="$HOME/PocketNoteLM"
cd "$REPO_DIR/frontend"

exec npm run preview
