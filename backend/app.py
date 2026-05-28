from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

@app.get("/api/hello")
async def hello():
    return {"message": "hello world"}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
