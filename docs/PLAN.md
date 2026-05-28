# Detailed Plan for the Project Management MVP

## Purpose

This plan defines the complete work stream for the Project Management MVP, including frontend and backend integration, authentication, persistence, AI connectivity, and final UI behavior. Each phase includes concrete substeps, success criteria, and verification tests.

## Existing state

- The frontend currently contains a working Kanban demo in `frontend/`
- Board state lives in local React state and is not persisted
- There is no backend yet in `backend/`
- There is no login flow or AI chat feature implemented

## Proposed JSON structure for the Kanban board

Use a simple schema that is easy to serialize into SQLite JSON and easy for the frontend and backend to share.

```json
{
  "userId": "user",
  "board": {
    "columns": [
      { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"] },
      { "id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"] }
    ],
    "cards": {
      "card-1": { "id": "card-1", "title": "Align roadmap themes", "details": "Draft quarterly themes..." }
    }
  },
  "updatedAt": "2026-05-11T12:00:00Z"
}
```

This schema supports:
- column renames
- card add / delete
- card reorder across columns
- easy JSON storage in SQLite
- user-specific board state for future multi-user support

## Phase 1: Plan and documentation

- [ ] Expand `docs/PLAN.md` with a detailed checklist and test criteria
- [ ] Create `frontend/agents.md` describing the existing frontend implementation
- [ ] Confirm the plan and the schema proposal with the user before writing code

Success criteria:
- `docs/PLAN.md` is complete and reviewed
- `frontend/agents.md` exists and accurately describes the code
- User approves the plan before implementation begins

## Phase 2: Scaffolding

Goal: establish a minimal backend container with FastAPI and static site support.

Tasks:
- [ ] Create `backend/` with FastAPI app entrypoint
- [ ] Add `Dockerfile` and `.dockerignore` at repo root
- [ ] Add `scripts/start.*` and `scripts/stop.*` for Windows/Mac/Linux
- [ ] Add backend route `/api/health` or `/api/hello` for a simple JSON response
- [ ] Add a static HTML route in FastAPI so the container can serve a minimal page
- [ ] Verify startup in Docker and confirm a known response from the backend route

Tests and verification:
- backend unit test for `/api/hello`
- Docker build/run should start without errors
- `curl http://localhost:<port>/api/hello` returns expected JSON

## Phase 3: Frontend build and static serving

Goal: make the existing Next.js demo build and serve from the backend.

Tasks:
- [ ] Confirm `frontend` build output via `npm run build`
- [ ] Configure backend to serve Next.js static output at `/`
- [ ] Ensure `frontend/src/app/page.tsx` renders the demo board when visited
- [ ] Preserve the existing drag/drop and add/delete behavior in the served app

Tests and verification:
- run `npm run build` successfully inside `frontend`
- backend server serves the built app at `/`
- browser or automated request to `/` returns HTML containing `Kanban Studio`

## Phase 4: Fake user sign in experience

Goal: require sign in before the Kanban board is visible.

Tasks:
- [ ] Add a login page or modal in the frontend
- [ ] Implement client-side auth state for the hardcoded credentials `user` / `password`
- [ ] Add login and logout flows
- [ ] Keep the board hidden until authentication succeeds
- [ ] Ensure sign-in state persists during the session until logout

Tests and verification:
- login accepts `user` / `password`
- login rejects invalid credentials
- logout returns user to the login screen
- authenticated users can see the board after login

## Phase 5: Database modeling

Goal: choose a lightweight, stable storage model for the Kanban board.

Tasks:
- [ ] Define the SQLite schema in `docs/` and implement it in `backend/`
- [ ] Use a single table for user boards with JSON content and timestamps
- [ ] Ensure the backend creates the database if it does not exist
- [ ] Document the DB design and the JSON schema in `docs/`

Proposed schema:
- table `boards`
  - `user_id TEXT PRIMARY KEY`
  - `board_json TEXT NOT NULL`
  - `updated_at TEXT NOT NULL`

Success criteria:
- the schema is documented in `docs/`
- the backend can create and open the database automatically
- board storage is stable and readable from the file system

## Phase 6: Backend API

Goal: add routes to read and update the Kanban board.

Tasks:
- [ ] Implement `GET /api/board` to return the signed-in user’s board JSON
- [ ] Implement `POST /api/board` to save board updates
- [ ] Implement `POST /api/auth/login` and `POST /api/auth/logout` if needed for future state handling
- [ ] Add backend validation for the JSON schema shape
- [ ] Keep the backend logic simple and minimal

Tests and verification:
- backend tests for `GET /api/board` and `POST /api/board`
- save/load roundtrip works for the same user
- invalid board payloads return 4xx errors

## Phase 7: Frontend + Backend integration

Goal: wire the frontend to load and save board state through the backend.

Tasks:
- [ ] Change frontend data flow to fetch board data from `GET /api/board`
- [ ] Use `POST /api/board` for column rename, card add/delete, and reorder events
- [ ] Keep the same UI and behaviors from the existing demo
- [ ] Add loading and error states as required for a smooth UX

Tests and verification:
- frontend loads the backend board after login
- changes in the UI are persisted by the backend
- reload restores the same board state

## Phase 8: AI connectivity

Goal: enable the backend to call OpenRouter and validate the connection.

Tasks:
- [ ] Add a backend AI route, such as `POST /api/ai/chat`
- [ ] Configure the backend to use `OPENROUTER_API_KEY` from `.env`
- [ ] Implement a simple API call to OpenRouter and return the response
- [ ] Validate the connection with a primitive test prompt such as `2+2`

Tests and verification:
- backend test verifies the AI request pipeline can be invoked
- the OpenRouter route returns a valid AI response
- errors are surfaced clearly if the API key is missing or invalid

## Phase 9: Structured output and board updates

Goal: make the AI return structured output that can optionally update the board.

Tasks:
- [ ] Define a minimal structured response format with fields for `message` and optional `boardUpdate`
- [ ] Ensure the backend sends the current board JSON and user query to the AI
- [ ] Parse the AI response and detect if a board update is included
- [ ] Apply safe board updates if the structure is valid

Suggested structured response format:
```json
{
  "message": "Updated the task.",
  "boardUpdate": {
    "columns": [ ... ],
    "cards": { ... }
  }
}
```

Tests and verification:
- end-to-end AI route returns the expected structured output
- `boardUpdate` is accepted only when valid
- the UI can refresh board state when AI changes are applied

## Phase 10: AI chat UI

Goal: add a sidebar chat experience that lets the AI update the Kanban board.

Tasks:
- [ ] Add a sidebar chat component in the frontend
- [ ] Allow users to send questions or instructions to the AI
- [ ] Send the current board JSON and conversation context to the backend AI route
- [ ] Display the AI response text in the UI
- [ ] If the AI returns `boardUpdate`, refresh the board automatically

Tests and verification:
- sidebar sends messages to the backend AI route
- AI reply appears in the chat UI
- board refreshes when AI returns structured updates
- UI remains functional after multiple AI requests

## Review and handoff

- [ ] Confirm the plan with the user before coding
- [ ] Keep the implementation minimal and focused on the MVP scope
- [ ] Avoid extra features beyond sign-in, persistence, and AI-driven board updates
- [ ] Use clear tests for each milestone
