# mynews

Tiny local web app that shows a brief of the latest TLDR AI newsletters. Training project.

- Backend: FastAPI. Frontend: one static HTML page. No database (in-memory cache, 15 min TTL).
- Endpoints: `/` (UI), `/api/news`, `/health`, `/version`.

## Run
```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt -r requirements-dev.txt
powershell scripts\run-dev.ps1        # http://127.0.0.1:8000
```

## Test (against a running app)
```
set BASE_URL=http://127.0.0.1:8000
.venv\Scripts\python -m pytest
```

## Package for deployment
```
.venv\Scripts\python scripts\package.py   # -> dist\mynews-<version>.zip
```
