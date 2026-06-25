from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3

import certifi
from dotenv import load_dotenv
import httpx
import truststore
truststore.inject_into_ssl()
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
DB_FILE = Path(__file__).parent / "kanban.db"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def create_database() -> None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS boards (
                user_id TEXT PRIMARY KEY,
                board_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_default_board(user_id: str) -> dict:
    return {
        "userId": user_id,
        "board": {"columns": [], "cards": {}},
        "updatedAt": utc_now(),
    }


def get_board_for_user(user_id: str) -> dict | None:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT board_json FROM boards WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return None

        board = json.loads(row["board_json"])
        updated = False

        if board.get("userId") != user_id:
            board["userId"] = user_id
            updated = True

        if "updatedAt" not in board:
            board["updatedAt"] = utc_now()
            updated = True

        if updated:
            save_board_for_user(user_id, board)

        return board


def save_board_for_user(user_id: str, board_data: dict) -> dict:
    board_data["userId"] = board_data.get("userId") or user_id
    board_data["updatedAt"] = utc_now()
    board_json = json.dumps(board_data)

    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO boards (user_id, board_json, updated_at) VALUES (?, ?, ?)",
            (user_id, board_json, board_data["updatedAt"]),
        )
        conn.commit()

    return board_data


create_database()


@app.get("/api/hello")
async def hello():
    return {"message": "hello world"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/board")
async def get_board():
    user_id = "user"
    board = get_board_for_user(user_id)

    if board is None:
        board = get_default_board(user_id)
        save_board_for_user(user_id, board)

    return board


@app.post("/api/board")
async def post_board(board_payload: dict = Body(...)):
    if not isinstance(board_payload, dict):
        raise HTTPException(status_code=400, detail="Board payload must be a JSON object.")

    user_id = "user"
    saved = save_board_for_user(user_id, board_payload)
    return saved


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are a Kanban board assistant. You help users manage their board by answering questions and making changes when asked.

Always respond with valid JSON in exactly this format:
{
  "message": "Your response to the user",
  "boardUpdate": null
}

If the user asks you to modify the board (add, move, delete, or rename cards or columns), include the complete updated board in boardUpdate:
{
  "message": "Description of what you changed",
  "boardUpdate": {
    "columns": [{"id": "...", "title": "...", "cardIds": ["..."]}],
    "cards": {"card-id": {"id": "...", "title": "...", "details": "..."}}
  }
}

Rules:
- boardUpdate must contain ALL columns and ALL cards, not just the changed ones
- Preserve existing IDs for existing items
- For new cards generate an id like "card-xyz123" (short random suffix)
- Only include boardUpdate when the user explicitly requests a board change
- Never include boardUpdate for read-only questions"""


def _is_valid_board_update(board_update: dict) -> bool:
    if not isinstance(board_update, dict):
        return False
    columns = board_update.get("columns")
    cards = board_update.get("cards")
    if not isinstance(columns, list) or not isinstance(cards, dict):
        return False
    for col in columns:
        if not all(k in col for k in ("id", "title", "cardIds")):
            return False
        if not isinstance(col["cardIds"], list):
            return False
    for card in cards.values():
        if not all(k in card for k in ("id", "title", "details")):
            return False
    return True


def _parse_ai_response(raw: str) -> dict:
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


@app.post("/api/ai/chat")
async def ai_chat(payload: dict = Body(...)):
    message = payload.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")

    user_id = "user"
    board_doc = get_board_for_user(user_id) or get_default_board(user_id)
    board_context = json.dumps(board_doc["board"], indent=2)

    system_with_board = f"{SYSTEM_PROMPT}\n\nCurrent board:\n{board_context}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": system_with_board},
                    {"role": "user", "content": message},
                ],
            },
            timeout=30.0,
        )
        response.raise_for_status()

    raw = response.json()["choices"][0]["message"]["content"]

    try:
        parsed = _parse_ai_response(raw)
        reply_message = parsed.get("message", raw)
        board_update = parsed.get("boardUpdate")
    except (json.JSONDecodeError, KeyError):
        reply_message = raw
        board_update = None

    if board_update is not None:
        if _is_valid_board_update(board_update):
            save_board_for_user(user_id, {"board": board_update})
        else:
            board_update = None

    return {"message": reply_message, "boardUpdate": board_update}


frontend_build_dir = Path(__file__).parent.parent / "frontend" / "out"
static_dir = frontend_build_dir if frontend_build_dir.exists() else Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
