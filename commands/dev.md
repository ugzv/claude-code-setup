---
description: Start dev server (kills port 3000 first)
---

Start the development server. Auto-detects project structure, kills existing processes, runs the right command.

## Modes

- `/dev` - Auto-detect and start (frontend, backend, or both if monorepo)
- `/dev --frontend` - Frontend only
- `/dev --backend` - Backend only
- `/dev --all` - Force both frontend and backend in parallel

## Smart Detection (check in order, use first match)

**Package.json scripts (fastest):**
- Has `dev` script → `pnpm dev` (done)
- Has `dev:frontend` / `dev:backend` → use those for flags
- Has workspaces with turbo → `pnpm dev` handles it

**No dev script? Detect framework:**
- `next.config.*` exists → `pnpm next dev`
- `vite.config.*` exists → `pnpm vite`
- `app.py` / `main.py` with uvicorn in deps → `uvicorn app:app --reload`
- `server.ts` / `server.js` → `pnpm tsx server.ts` or `node server.js`

**Monorepo detection:**
- `frontend/` + `backend/` dirs → treat as --all by default
- `apps/web` + `apps/api` → same

## Ports

Kill before starting:
- Frontend: 3000, 5173
- Backend: 3001, 8000

```bash
lsof -ti:3000,3001,5173,8000 | xargs kill -9 2>/dev/null || true
```

## Execution

1. Parse `$ARGUMENTS` for flags
2. One quick scan: check `package.json` scripts + look for config files
3. Kill relevant ports
4. Run (background shells for --all, foreground for single)

Be fast - don't over-scan. First match wins.

$ARGUMENTS
