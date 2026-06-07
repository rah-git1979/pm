import json
import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from backend.app import app, DB_FILE

client = TestClient(app)

def test_hello_endpoint():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "hello world"}


def test_get_board_returns_valid_board():
    response = client.get("/api/board")
    assert response.status_code == 200

    data = response.json()
    assert data["userId"] == "user"
    assert isinstance(data["board"]["columns"], list)
    assert isinstance(data["board"]["cards"], dict)
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


def _mock_openrouter(reply: str):
    mock_response = MagicMock()
    mock_response.json.return_value = {"choices": [{"message": {"content": reply}}]}
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_response)
    return mock_client


def test_ai_chat_returns_reply(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    with patch("httpx.AsyncClient", return_value=_mock_openrouter("4")):
        response = client.post("/api/ai/chat", json={"message": "2+2"})
    assert response.status_code == 200
    assert response.json()["reply"] == "4"


def test_ai_chat_missing_message(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    response = client.post("/api/ai/chat", json={"message": ""})
    assert response.status_code == 400


def test_ai_chat_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    response = client.post("/api/ai/chat", json={"message": "hello"})
    assert response.status_code == 500


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
