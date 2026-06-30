from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.schemas import BoardDocumentModel, BoardResponse


DEFAULT_USER_ID = "user-1"
DEFAULT_USERNAME = "user"
DEFAULT_BOARD_ID = "board-1"
DEFAULT_BOARD_NAME = "Kanban Studio"

DEFAULT_BOARD_DOCUMENT = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Database:
    def __init__(self, path: str):
        self.path = path

    @contextmanager
    def connect(self):
        database_path = Path(self.path)
        database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
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
                """
            )

            now = utc_now()
            connection.execute(
                """
                INSERT INTO users (id, username, display_name, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(username) DO NOTHING
                """,
                (DEFAULT_USER_ID, DEFAULT_USERNAME, "MVP User", now, now),
            )

            board_exists = connection.execute(
                "SELECT 1 FROM boards WHERE user_id = ?",
                (DEFAULT_USER_ID,),
            ).fetchone()

            if not board_exists:
                connection.execute(
                    """
                    INSERT INTO boards (id, user_id, name, board_json, version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                    """,
                    (
                        DEFAULT_BOARD_ID,
                        DEFAULT_USER_ID,
                        DEFAULT_BOARD_NAME,
                        json.dumps(DEFAULT_BOARD_DOCUMENT),
                        now,
                        now,
                    ),
                )

    def fetch_board_row(self) -> sqlite3.Row | None:
        with self.connect() as connection:
            return connection.execute(
                "SELECT id, user_id, name, board_json, updated_at FROM boards WHERE user_id = ?",
                (DEFAULT_USER_ID,),
            ).fetchone()

    def upsert_board(self, board_id: str, name: str, board_document: dict) -> BoardResponse:
        now = utc_now()
        with self.connect() as connection:
            current = connection.execute(
                "SELECT created_at FROM boards WHERE user_id = ?",
                (DEFAULT_USER_ID,),
            ).fetchone()

            if current:
                connection.execute(
                    """
                    UPDATE boards
                    SET id = ?, name = ?, board_json = ?, version = version + 1, updated_at = ?
                    WHERE user_id = ?
                    """,
                    (board_id, name, json.dumps(board_document), now, DEFAULT_USER_ID),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO boards (id, user_id, name, board_json, version, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 1, ?, ?)
                    """,
                    (board_id, DEFAULT_USER_ID, name, json.dumps(board_document), now, now),
                )

        return self.read_board_response()

    def delete_board(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM boards WHERE user_id = ?", (DEFAULT_USER_ID,))

    def read_board_response(self) -> BoardResponse:
        row = self.fetch_board_row()
        if row is None:
            raise LookupError("Board not found.")
        board_document = BoardDocumentModel.model_validate_json(row["board_json"])
        return BoardResponse(
            id=row["id"],
            userId=row["user_id"],
            name=row["name"],
            columns=board_document.columns,
            cards=board_document.cards,
            updatedAt=row["updated_at"],
        )