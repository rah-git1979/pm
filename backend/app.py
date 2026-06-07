from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3

from dotenv import load_dotenv
import httpx
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
        "updatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
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
            board["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            updated = True

        if updated:
            save_board_for_user(user_id, board)

        return board


def save_board_for_user(user_id: str, board_data: dict) -> dict:
    board_data["userId"] = board_data.get("userId") or user_id
    board_data["updatedAt"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
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


@app.post("/api/ai/chat")
async def ai_chat(payload: dict = Body(...)):
    message = payload.get("message", "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="message is required")

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not configured")

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": OPENROUTER_MODEL,
                "messages": [{"role": "user", "content": message}],
            },
            timeout=30.0,
        )
        response.raise_for_status()

    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    return {"reply": reply}


frontend_build_dir = Path(__file__).parent.parent / "frontend" / "out"
static_dir = frontend_build_dir if frontend_build_dir.exists() else Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
