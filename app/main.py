from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import feed

APP_DIR = Path(__file__).parent
VERSION_FILE = APP_DIR.parent / "VERSION"

app = FastAPI(title="mynews")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")


def read_version() -> str:
    try:
        return VERSION_FILE.read_text().strip()
    except OSError:
        return "unknown"


@app.get("/")
def index():
    return FileResponse(APP_DIR / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": read_version()}


@app.get("/api/news")
def news():
    try:
        return feed.get_news()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"feed unavailable: {exc}")
