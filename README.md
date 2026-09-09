# VesperSignal News

News discovery and AI-assisted research, extracted from the VesperSignal project.

## Problem

Students and researchers spend time opening many tabs, comparing articles and keeping references. This demo brings discovery, source excerpts, concise AI summaries and saved notes into one workflow. AI helps screen sources; it does not replace checking the original publication.

## Included

- Vietnamese and English news feed, categories and article details.
- RSS ingestion and topic discovery across configured web and research providers.
- AI summaries and multi-source synthesis with numbered source references.
- Saved articles, research notes, reading history and exports in the browser.
- Feedback collection; backend MVP endpoints for story grouping, interests and email digest previews.
- Account/session support for authenticated research and usage limits.

Stock dashboards, market data jobs, model training and standalone AI chat are excluded. News UI is retained.

## Run locally

Use Python 3.12+, Node.js 20+ and PostgreSQL (Neon works).

1. Copy `backend/.env.example` to `backend/.env` and configure your database and a random gateway secret.
2. Copy `frontend/.env.example` to `frontend/.env.local`, using the same gateway secret.
3. Start Ollama with the configured model available (`qwen2.5:3b` by default).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir backend --port 8001
```

In another terminal:

```powershell
cd frontend
npm ci
npm run dev -- --port 3003
```

Open http://localhost:3003/news. Database migrations run on backend startup. Use one backend worker while ingestion runs in-process.

## Render deployment

Create two Web Services from this repository (the frontend needs its server API routes; it is not a static export):

| Setting | Backend | Frontend |
| --- | --- | --- |
| Root directory | `backend` | `frontend` |
| Build command | `pip install -r requirements.txt` | `npm ci && npm run build` |
| Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` | `npm run start -- --hostname 0.0.0.0 --port $PORT` |
| Health path | `/health` | `/news` |

Set environment values in the hosting dashboard, never in committed files. Set frontend `BACKEND_URL` to the backend HTTPS URL and share `CHAT_PROXY_TOKEN` between services. Backend needs `DATABASE_URL` and AI configuration.

**Local Ollama is not reachable from Render at localhost.** Remote AI is not configured by this repository upload. To use your personal computer, a separately configured authenticated HTTPS gateway/tunnel is required, and the computer must remain online. Do not expose Ollama directly to the internet. Until then, AI works locally only; do not claim hosted AI is ready.

## Limits and privacy

Search covers available providers, not every page on the internet. Summaries use collected excerpts and can fail or omit context. Citation validation checks reference structure, not factual truth. Background updates require a running backend; a sleeping service cannot guarantee continuous ingestion. Daily usage limits still apply to local AI. Email delivery is disabled by default and requires SMTP configuration and consent. Browser history/notes remain on that browser; PostgreSQL stores articles, accounts and submitted feedback. No personal data, API tokens, database dump or model weights are included in this repo.

See [project rationale](NEWS_PROJECT.md) and [backend MVP notes](NEWS_MVP.md).

## Checks

```powershell
$env:PYTHONPATH='backend'
python -m unittest discover -s backend/tests/unit
cd frontend
npm run build
```
