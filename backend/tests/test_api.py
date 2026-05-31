import json
import sqlite3
from fastapi.testclient import TestClient
from backend.app import app, DB_FILE

client = TestClient(app)

def test_hello_endpoint():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}


def test_get_board_returns_default_board():
    response = client.get("/api/board")
    assert response.status_code == 200

    data = response.json()
    assert data["userId"] == "user"
    assert data["board"]["columns"] == []
    assert data["board"]["cards"] == {}
    assert "updatedAt" in data

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "SELECT board_json FROM boards WHERE user_id = ?",
            ("user",),
        )
        row = cursor.fetchone()
        assert row is not None
        assert json.loads(row[0]) == data


def test_post_board_updates_board():
    payload = {
        "board": {
            "columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": []}],
            "cards": {},
        }
    }

    response = client.post("/api/board", json=payload)
    assert response.status_code == 200

    saved = response.json()
    assert saved["userId"] == "user"
    assert saved["board"] == payload["board"]
    assert "updatedAt" in saved

    response = client.get("/api/board")
    assert response.status_code == 200
    assert response.json()["board"] == payload["board"]


def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Kanban Studio" in response.text


def test_database_created():
    assert DB_FILE.exists()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='boards'"
        )
        assert cursor.fetchone() is not None


def test_board_json_storage():
    sample_user = "user"
    sample_board = '{"board": {"columns": [], "cards": {}}}'
    timestamp = "2026-05-28T00:00:00Z"

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO boards (user_id, board_json, updated_at) VALUES (?, ?, ?)",
            (sample_user, sample_board, timestamp),
        )
        conn.commit()

        cursor = conn.execute(
            "SELECT board_json, updated_at FROM boards WHERE user_id = ?",
            (sample_user,),
        )
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == sample_board
        assert row[1] == timestamp
