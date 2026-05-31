# Database Schema for Project Management MVP

## SQLite storage

The backend stores the user board in a single SQLite database file:

- `backend/kanban.db`

The schema uses one table:

- `boards`

### Table: `boards`

Columns:

- `user_id TEXT PRIMARY KEY`
- `board_json TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

This table stores one board per user with the board state saved as JSON.

### Example SQL

```sql
CREATE TABLE IF NOT EXISTS boards (
  user_id TEXT PRIMARY KEY,
  board_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
```

## JSON payload structure

The frontend and backend share a simple board JSON format.

### Example board JSON

```json
{
  "userId": "user",
  "board": {
    "columns": [
      {
        "id": "col-backlog",
        "title": "Backlog",
        "cardIds": ["card-1", "card-2"]
      },
      {
        "id": "col-discovery",
        "title": "Discovery",
        "cardIds": ["card-3"]
      }
    ],
    "cards": {
      "card-1": {
        "id": "card-1",
        "title": "Align roadmap themes",
        "details": "Draft quarterly themes and align stakeholders."
      },
      "card-2": {
        "id": "card-2",
        "title": "Write launch plan",
        "details": "Create timeline and communication plan."
      }
    }
  },
  "updatedAt": "2026-05-28T12:00:00Z"
}
```

## Notes

- `user_id` is the primary key for the table and matches the hardcoded user in the current MVP.
- `board_json` stores the full serialized board state.
- `updated_at` is stored as an ISO 8601 UTC timestamp.
- The backend creates the database automatically when starting, using `backend/app.py`.

## Current backend implementation

The created database schema is implemented in `backend/app.py` with the `create_database()` function.
