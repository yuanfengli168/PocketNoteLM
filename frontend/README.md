# Frontend — PocketNoteLM

React + Vite + TypeScript chat UI.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production. Any push to `main` that touches `frontend/` triggers the GitHub Actions deploy. |

**Always branch off `main` for new frontend work**, e.g. `git checkout -b feat/my-feature`.

---

## Local Development

```bash
cd frontend
npm install       # first time only
npm run dev       # dev server at http://localhost:5173 (hot reload)
```

Create a `.env` file from the example before running:

```bash
cp .env.example .env
# Edit VITE_API_URL to point to the running backend
```

---

## Production Build & Local Hosting

The app is served locally via `vite preview`. It can auto-start on login via `launchd` (see below).

```bash
npm run build     # compile to dist/
npm run preview   # serve dist/ at http://localhost:4172
```

### launchd service (macOS auto-start)

The service is registered as `com.pocketnotelm.frontend`.

```bash
# Check status
launchctl list | grep pocketnotelm

# Stop
launchctl unload ~/Library/LaunchAgents/com.pocketnotelm.frontend.plist

# Start
launchctl load ~/Library/LaunchAgents/com.pocketnotelm.frontend.plist

# Logs
cat /tmp/pocketnotelm-frontend.log
cat /tmp/pocketnotelm-frontend-error.log
```

The plist file lives at:
`launchd/com.pocketnotelm.frontend.plist` (in repo)
`~/Library/LaunchAgents/com.pocketnotelm.frontend.plist` (active copy)

The startup script lives at `~/pocketnotelm-start-frontend.sh` — do not delete it.

---

## GitHub Actions Deploy

When the repo is public, every push to `main` touching `frontend/**` auto-deploys to GitHub Pages via `.github/workflows/deploy-frontend.yml`.

**Required one-time GitHub setup:**
1. Repo → Settings → Pages → Source: `gh-pages` branch, `/ (root)`
2. Add a repository variable `VITE_API_URL` (Settings → Variables → Actions)
3. Add a repository secret `VITE_ADMIN_TOKEN` (Settings → Secrets → Actions)

**Live URL:** `https://YOUR_USERNAME.github.io/PocketNoteLM/`

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend base URL | `http://localhost:8000` |
| `VITE_ADMIN_TOKEN` | Token for the Stop Service button | `some-secret-token` |

Never commit `.env` — it is gitignored.
