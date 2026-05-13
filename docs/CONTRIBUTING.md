# Contributing to PocketNoteLM

Thank you for your interest in contributing!

## How to contribute

1. **Fork** the repo and create a branch from `main`
2. **Make your changes** — keep PRs focused on a single feature or fix
3. **Test locally** — run the backend and frontend before submitting
4. **Open a Pull Request** — describe what you changed and why

## Development setup

See the [README](README.md) for full setup instructions. The short version:

```bash
zsh install.sh
```

## What we're looking for

- Bug fixes
- Improved RAG quality (chunking, retrieval, prompts)
- New document format support
- Performance improvements on Apple Silicon
- Better install / setup UX
- Tests

## Code style

- Python: [ruff](https://docs.astral.sh/ruff/) for linting and formatting
- TypeScript: Prettier + ESLint (configured in `frontend/`)

## Reporting issues

Open a GitHub Issue with:
- macOS version and chip (e.g. M2 Pro, 32 GB)
- Ollama version (`ollama --version`)
- The model you're using
- Steps to reproduce

## License

By contributing, you agree your contributions will be licensed under the [MIT License](LICENSE).
