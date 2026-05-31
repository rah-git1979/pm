# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Kanban Studio — a project management MVP. NextJS frontend, Python FastAPI backend, packaged in Docker. The backend serves both the API and the static frontend build.

MVP constraints: one hardcoded user (`user` / `password`), one board per user, runs locally in Docker.

## Commands

### Frontend (run from `frontend/`)
```bash
npm install
npm run dev              # dev server on http://127.0.0.1:3000
npm run build:static     # static export (for Docker)
npm run test:unit        # vitest unit tests
npm run test:e2e         # playwright E2E (starts dev server automatically)
npm run test:all         # both unit + E2E
```

### Backend (run from project root)
```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload   # dev server on http://localhost:8000
pytest backend/tests/              # backend tests
```

### Docker (Windows PowerShell)
```powershell
./scripts/start.ps1     # builds image and starts container on http://localhost:8000
./scripts/stop.ps1      # stops and removes the container
```

## Architecture

### Request flow
Browser → FastAPI (port 8000) → serves static frontend at `/`, API endpoints at `/api/*`

In development, the frontend dev server (port 3000) proxies API calls to the FastAPI backend. In Docker, FastAPI serves the static Next.js export from `frontend/out/` (falls back to `backend/static/`).

### Backend (`backend/app.py`)
Single-file FastAPI app. SQLite database at `backend/kanban.db`. Board data is stored as a JSON blob keyed by `user_id`.

Board document shape:
```json
{ "userId": "user", "board": { "columns": [], "cards": {} }, "updatedAt": "..." }
```

No auth middleware — `user_id` is hardcoded to `"user"` for all endpoints. The DB schema supports multiple users for future use.

### Frontend (`frontend/src/`)
- `app/page.tsx` — root page; renders `LoginPanel` or `KanbanBoard` based on `sessionStorage`
- `components/KanbanBoard.tsx` — board state, DnD context (`@dnd-kit`), column/card operations
- `components/KanbanColumn.tsx` — single column with inline rename and add-card form
- `components/KanbanCard.tsx` — individual card with delete
- `lib/kanban.ts` — `BoardData`, `Column`, `Card` types; `moveCard`, `createId` helpers

Auth is purely frontend: login sets `sessionStorage["kanban-authenticated"] = "true"`, logout clears it.

### AI feature
Uses OpenRouter (`OPENROUTER_API_KEY` in `.env`). Model: `openai/gpt-oss-120b`. AI chat lives in a sidebar and can create/edit/move cards.

## Color scheme
```
Accent Yellow:    #ecad0a   (accent lines, highlights)
Blue Primary:     #209dd7   (links, key sections)
Purple Secondary: #753991   (submit buttons, important actions)
Dark Navy:        #032147   (main headings)
Gray Text:        #888888   (supporting text, labels)
```

## Coding standards
- Keep it simple — never over-engineer, no unnecessary defensive programming, no extra features
- Use latest versions of libraries and idiomatic approaches
- No emojis anywhere
- When hitting issues, identify root cause with evidence before fixing
- Minimal documentation; README stays short
