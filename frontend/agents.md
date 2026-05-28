# Frontend agent notes

## Purpose

This document describes the current frontend code in `frontend/` and the existing implementation state for the next phase of the Project Management MVP.

## Existing frontend architecture

- `package.json`
  - Next.js 16 + React 19
  - `@dnd-kit/*` for drag-and-drop
  - Tailwind CSS 4 for styling
  - `vitest` for unit tests and `@playwright/test` for E2E
  - `npm run dev`, `npm run build`, `npm run start`

- `src/app/page.tsx`
  - Minimal page entrypoint
  - Renders `KanbanBoard`

## Key components

- `src/components/KanbanBoard.tsx`
  - Holds board state in React local state
  - Uses `DndContext` from `@dnd-kit/core` to support drag and drop
  - Supports renaming columns, adding cards, deleting cards, and moving cards between columns
  - Uses `KanbanColumn`, `KanbanCardPreview`, and helper functions from `src/lib/kanban.ts`

- `src/components/KanbanColumn.tsx`
  - Renders a single column
  - Displays cards within the column
  - Includes inline column rename input and add-card form
  - Emits callback props to update board state in `KanbanBoard`

- `src/components/KanbanCard.tsx`
  - Renders an individual card
  - Includes a delete button wired through props

- `src/components/KanbanCardPreview.tsx`
  - Shows a preview of a dragged card in the drag overlay

- `src/lib/kanban.ts`
  - Defines the board model: `Card`, `Column`, and `BoardData`
  - Exposes `initialData` seed data for the demo board
  - Exposes `moveCard` helper for reordering and moving cards across columns
  - Exposes `createId` to generate new card IDs

## Current behavior

- The app is a standalone frontend demo
- No backend integration exists yet
- The board state is not persisted across page reloads
- There is no authentication or AI chat UI implemented in this folder

## Existing tests

- `src/components/KanbanBoard.test.tsx`
  - Verifies five columns render
  - Ensures column renaming works
  - Tests adding and deleting a card in the first column

## Notes for next work

- This demo is a strong starting point for wiring backend persistence and AI-driven updates
- The frontend currently has a clean separation between board state, UI, and drag-and-drop helpers
- The next step should keep the same component structure while replacing local state with backend-powered data and authentication
