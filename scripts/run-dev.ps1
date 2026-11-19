# Run mynews from this checkout (development). The deployer MCP uses its own runtime folder.
& "$PSScriptRoot\..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir "$PSScriptRoot\.."
