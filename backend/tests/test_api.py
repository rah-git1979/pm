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


SAMPLE_BOARD_UPDATE = {
    "columns": [{"id": "col-backlog", "title": "Backlog", "cardIds": ["card-new"]}],
    "cards": {"card-new": {"id": "card-new", "title": "New task", "details": "Details here."}},
}


def test_ai_chat_returns_message_without_board_update(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    ai_reply = json.dumps({"message": "You have 5 columns.", "boardUpdate": None})
    with patch("backend.app.httpx.AsyncClient", return_value=_mock_openrouter(ai_reply)):
        response = client.post("/api/ai/chat", json={"message": "How many columns do I have?"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "You have 5 columns."
    assert data["boardUpdate"] is None


def test_ai_chat_returns_board_update_and_saves(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    ai_reply = json.dumps({"message": "Added New task.", "boardUpdate": SAMPLE_BOARD_UPDATE})
    with patch("backend.app.httpx.AsyncClient", return_value=_mock_openrouter(ai_reply)):
        response = client.post("/api/ai/chat", json={"message": "Add a card called New task"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Added New task."
    assert data["boardUpdate"] == SAMPLE_BOARD_UPDATE

    # Verify board was saved to DB
    board_response = client.get("/api/board")
    assert board_response.json()["board"] == SAMPLE_BOARD_UPDATE


def test_ai_chat_ignores_invalid_board_update(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    ai_reply = json.dumps({"message": "Done.", "boardUpdate": {"bad": "data"}})
    with patch("backend.app.httpx.AsyncClient", return_value=_mock_openrouter(ai_reply)):
        response = client.post("/api/ai/chat", json={"message": "Do something"})
    assert response.status_code == 200
    assert response.json()["boardUpdate"] is None


def test_ai_chat_handles_markdown_wrapped_json(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    ai_reply = "```json\n" + json.dumps({"message": "Got it.", "boardUpdate": None}) + "\n```"
    with patch("backend.app.httpx.AsyncClient", return_value=_mock_openrouter(ai_reply)):
        response = client.post("/api/ai/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json()["message"] == "Got it."


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
