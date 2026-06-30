# Database design

## Goal

This document defines the MVP persistence model for users, board state, and future AI chat history.

The design goal is simplicity first:

- keep the frontend payload close to the current in-memory `BoardData` shape
- use SQLite locally with automatic initialization
- support board load, column rename, card create/edit/delete, and card moves without complex joins
- leave room for later AI chat persistence without forcing it into the first board implementation

## Recommended persistence approach

Persist each user's board as a single JSON document plus lightweight relational metadata.

This means:

- `users` stays relational
- `boards` stores one row per user board
- `boards.board_json` stores the board structure used by the frontend
- `chat_messages` stays relational because chat history is append-oriented and easier to query that way

## Why this approach

This is the best MVP fit for the current requirements.

- The board already exists in the frontend as a single object with `columns` and `cards`.
- The MVP has one board per signed-in user.
- Users can have different numbers of columns, so keeping the board as a single document avoids unnecessary column and card join complexity.
- AI operations will likely read and update the whole board state, which maps naturally to a document payload.
- SQLite handles this pattern well enough for a local MVP.

## Schema summary

### `users`

Purpose: store known users and allow future growth beyond the single MVP user.

Suggested columns:

- `id TEXT PRIMARY KEY`
- `username TEXT NOT NULL UNIQUE`
- `display_name TEXT`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Suggested seed row for MVP:

- `id = 'user-1'`
- `username = 'user'`
- `display_name = 'MVP User'`

### `boards`

Purpose: store one persisted board per user.

Suggested columns:

- `id TEXT PRIMARY KEY`
- `user_id TEXT NOT NULL UNIQUE`
- `name TEXT NOT NULL`
- `board_json TEXT NOT NULL`
- `version INTEGER NOT NULL DEFAULT 1`
- `created_at TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Constraints:

- `FOREIGN KEY (user_id) REFERENCES users(id)`
- unique `user_id` because MVP allows one board per user

### `chat_messages`

Purpose: store chat history for the AI sidebar when Parts 8 and 9 are implemented.

Suggested columns:

- `id TEXT PRIMARY KEY`
- `user_id TEXT NOT NULL`
- `board_id TEXT NOT NULL`
- `role TEXT NOT NULL`
- `message_text TEXT NOT NULL`
- `tool_result_json TEXT`
- `created_at TEXT NOT NULL`

Constraints:

- `FOREIGN KEY (user_id) REFERENCES users(id)`
- `FOREIGN KEY (board_id) REFERENCES boards(id)`
- `role` should be limited in application validation to `user`, `assistant`, or `system`

## SQLite DDL

```sql
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS boards (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    board_json TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    board_id TEXT NOT NULL,
    role TEXT NOT NULL,
    message_text TEXT NOT NULL,
    tool_result_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (board_id) REFERENCES boards(id)
);
```

## Board JSON payload

The persisted board JSON should stay close to the current frontend shape.

Suggested persisted payload inside `boards.board_json`:

```json
{
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
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-4", "card-5"]
    },
    {
      "id": "col-review",
      "title": "Review",
      "cardIds": ["card-6"]
    },
    {
      "id": "col-done",
      "title": "Done",
      "cardIds": ["card-7", "card-8"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Align roadmap themes",
      "details": "Draft quarterly themes with impact statements and metrics."
    }
  }
}
```

### Payload rules

- `columns` order is the canonical board column order.
- Column IDs must remain stable once seeded.
- Users may have different numbers of columns.
- Column titles are editable.
- `cardIds` defines the card order inside each column.
- Every `cardId` in `cardIds` must exist in `cards`.
- Cards not referenced by any column are invalid.

## API response shape recommendation

For Part 6 and Part 7, the backend should return a small wrapper around the board JSON instead of returning raw database rows.

Suggested response for `GET /api/board`:

```json
{
  "id": "board-1",
  "userId": "user-1",
  "name": "Kanban Studio",
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Align roadmap themes",
      "details": "Draft quarterly themes with impact statements and metrics."
    }
  },
  "updatedAt": "2026-06-30T12:00:00Z"
}
```

This keeps the frontend mapping straightforward because `columns` and `cards` can still be consumed almost exactly as they are today.

## Mapping from JSON to SQLite

The mapping should be:

- `users` row identifies the owner
- `boards.id`, `boards.user_id`, `boards.name`, timestamps, and version stay in relational columns
- `boards.board_json` stores the actual board structure
- `chat_messages` stores individual sidebar messages and any structured AI result payload

In practice, the backend reads one `boards` row, parses `board_json`, and returns a merged API response.

## Initialization and migration expectations

The backend should initialize the database automatically on startup.

Expected startup behavior:

- create the SQLite file if it does not exist
- create tables if they do not exist
- seed the default MVP user if missing
- seed the default board for that user if missing

Migration expectations for MVP:

- keep migrations simple and code-driven at startup
- use `CREATE TABLE IF NOT EXISTS` for the first implementation
- treat `version` on `boards` as board-document versioning, not schema migration state
- if schema evolution begins to exceed simple startup SQL, introduce a real migration tool later

Suggested initial database file location:

- backend-local default such as `backend/data/app.db`
- overrideable by environment variable in Part 6

## Impact on endpoint design

Because the board is stored as a JSON document, column and card endpoints should mutate the board document and then write the full updated JSON back to `boards.board_json`.

That means the API can still be resource-oriented without requiring normalized board tables.

Examples:

- rename column: load board document, update one column title, save document
- add card: load board document, add card object, append card ID to one column, save document
- move card: load board document, update source and destination `cardIds`, save document

## Recommended Part 6 endpoint style

Use targeted endpoints for column and card actions, but treat each write as a full board-document rewrite in the persistence layer.

Recommended MVP endpoints:

- `GET /api/board` returns the seeded user's board payload
- `POST /api/columns` creates a column and returns the updated board
- `PATCH /api/columns/{columnId}` renames a column and returns the updated board
- `DELETE /api/columns/{columnId}` deletes a column and returns the updated board
- `POST /api/cards` creates a card in a target column and returns the updated board
- `PATCH /api/cards/{cardId}` updates card fields and returns the updated board
- `DELETE /api/cards/{cardId}` deletes a card and returns the updated board
- `POST /api/cards/{cardId}/move` moves a card and returns the updated board

Why this is the right Part 6 tradeoff:

- the frontend can call direct, intention-revealing endpoints instead of sending whole-board replacements for every interaction
- the backend keeps persistence simple because it only needs to validate and rewrite one JSON document per update
- the response shape can stay consistent by returning the full board after each mutation

## Local persistence note for Docker

If SQLite is stored only inside the backend container filesystem, data will be lost when that container is recreated.

For Part 6, the backend should therefore:

- default the database path to a writable app-local directory such as `/app/data/app.db`
- allow that path to be overridden by environment variable
- mount that directory from Compose using a named volume or bind mount so local persistence survives container recreation

## Important MVP constraint

The product decision is now that column count is not fixed per user.

Because of that, the implementation should treat columns as full board resources that can be:

- created
- renamed
- deleted
- returned in a stable stored order

The `columns` array remains the canonical source of display order, but the number of columns must be allowed to vary by board.

## Recommendation

Approve the JSON-document board approach for Part 6.

It is the simplest design that:

- matches the current frontend state shape
- keeps the backend implementation small
- supports AI-driven whole-board edits later
- avoids unnecessary relational complexity for the MVP

## Sign-off questions

Before Part 6 starts, confirm these points:

1. Persist one board per user as a single JSON document in `boards.board_json`.
2. Keep `users` and `chat_messages` as normal relational tables.
3. Allow each user board to have a variable number of columns.
4. Keep column create, rename, and delete in scope for MVP persistence.
5. Seed the default `user` account and one default board automatically on startup.