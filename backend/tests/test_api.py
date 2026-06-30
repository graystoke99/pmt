from pathlib import Path

from fastapi.testclient import TestClient
import sqlite3

from app.main import create_app
from app.config import Settings


def create_test_client(database_path: Path) -> TestClient:
    settings = Settings(database_path=str(database_path))
    app = create_app(settings)
    return TestClient(app)


def test_initialization_creates_schema_and_seed_data(tmp_path: Path):
    database_path = tmp_path / "app.db"

    with create_test_client(database_path) as client:
        response = client.get("/api/board")

    assert response.status_code == 200
    payload = response.json()
    assert payload["userId"] == "user-1"
    assert payload["name"] == "Kanban Studio"

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert {"users", "boards", "chat_messages"}.issubset(tables)


def test_board_create_read_update_delete(tmp_path: Path):
    database_path = tmp_path / "app.db"

    with create_test_client(database_path) as client:
        delete_response = client.delete("/api/board")
        assert delete_response.status_code == 204

        read_missing = client.get("/api/board")
        assert read_missing.status_code == 404

        create_response = client.post(
            "/api/board",
            json={
                "name": "Recovery Board",
                "columns": [{"id": "col-one", "title": "One", "cardIds": ["card-one"]}],
                "cards": {
                    "card-one": {
                        "id": "card-one",
                        "title": "Restore board",
                        "details": "Create the board again.",
                    }
                },
            },
        )
        assert create_response.status_code == 201
        assert create_response.json()["name"] == "Recovery Board"

        update_response = client.put(
            "/api/board",
            json={
                "name": "Updated Board",
                "columns": [{"id": "col-one", "title": "Only", "cardIds": ["card-one"]}],
                "cards": {
                    "card-one": {
                        "id": "card-one",
                        "title": "Updated card",
                        "details": "Updated details.",
                    }
                },
            },
        )
        assert update_response.status_code == 200
        updated_payload = update_response.json()
        assert updated_payload["name"] == "Updated Board"
        assert updated_payload["columns"][0]["title"] == "Only"
        assert updated_payload["cards"]["card-one"]["title"] == "Updated card"


def test_column_crud(tmp_path: Path):
    database_path = tmp_path / "app.db"

    with create_test_client(database_path) as client:
        create_response = client.post("/api/columns", json={"title": "Blocked"})
        assert create_response.status_code == 201
        payload = create_response.json()
        created_column = next(column for column in payload["columns"] if column["title"] == "Blocked")

        update_response = client.patch(
            f"/api/columns/{created_column['id']}",
            json={"title": "Blocked by vendor"},
        )
        assert update_response.status_code == 200
        renamed = next(
            column for column in update_response.json()["columns"] if column["id"] == created_column["id"]
        )
        assert renamed["title"] == "Blocked by vendor"

        delete_response = client.delete(f"/api/columns/{created_column['id']}")
        assert delete_response.status_code == 200
        remaining_ids = {column["id"] for column in delete_response.json()["columns"]}
        assert created_column["id"] not in remaining_ids


def test_card_crud(tmp_path: Path):
    database_path = tmp_path / "app.db"

    with create_test_client(database_path) as client:
        create_response = client.post(
            "/api/cards",
            json={
                "columnId": "col-backlog",
                "title": "Add backend API",
                "details": "Persist board changes.",
            },
        )
        assert create_response.status_code == 201
        created_payload = create_response.json()
        created_card_id = next(
            card_id
            for card_id, card in created_payload["cards"].items()
            if card["title"] == "Add backend API"
        )

        update_response = client.patch(
            f"/api/cards/{created_card_id}",
            json={"title": "Add persistent backend API", "details": "Ship Part 6."},
        )
        assert update_response.status_code == 200
        updated_card = update_response.json()["cards"][created_card_id]
        assert updated_card["title"] == "Add persistent backend API"
        assert updated_card["details"] == "Ship Part 6."

        delete_response = client.delete(f"/api/cards/{created_card_id}")
        assert delete_response.status_code == 200
        assert created_card_id not in delete_response.json()["cards"]


def test_move_card_between_columns(tmp_path: Path):
    database_path = tmp_path / "app.db"

    with create_test_client(database_path) as client:
        response = client.post(
            "/api/cards/card-1/move",
            json={"targetColumnId": "col-review", "targetIndex": 0},
        )

    assert response.status_code == 200
    payload = response.json()
    backlog = next(column for column in payload["columns"] if column["id"] == "col-backlog")
    review = next(column for column in payload["columns"] if column["id"] == "col-review")
    assert "card-1" not in backlog["cardIds"]
    assert review["cardIds"][0] == "card-1"


def test_invalid_payload_handling(tmp_path: Path):
    database_path = tmp_path / "app.db"

    with create_test_client(database_path) as client:
        invalid_replace = client.put(
            "/api/board",
            json={
                "name": "Broken Board",
                "columns": [{"id": "col-one", "title": "One", "cardIds": ["missing-card"]}],
                "cards": {},
            },
        )
        assert invalid_replace.status_code == 409

        invalid_card = client.post(
            "/api/cards",
            json={"columnId": "missing-column", "title": "Bad target", "details": "No column."},
        )
        assert invalid_card.status_code == 404

        invalid_shape = client.post("/api/cards", json={"columnId": "col-backlog", "details": "Missing title"})
        assert invalid_shape.status_code == 422