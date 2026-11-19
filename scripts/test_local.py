"""Run the test suite against THIS checkout: start the app on a free port, run pytest, stop the app.

Usage (from the repo root):  <python> scripts/test_local.py [pytest args...]
Exit code is pytest's exit code. Used by the implementing agent to verify its work before packaging.
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_healthy(url: str, proc: subprocess.Popen, timeout: float = 25.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline and proc.poll() is None:
        try:
            with urllib.request.urlopen(url + "/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def main() -> int:
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_healthy(base, server):
            print(f"app did not become healthy on {base}", file=sys.stderr)
            return 3
        env = {**os.environ, "BASE_URL": base}
        return subprocess.run([sys.executable, "-m", "pytest", "-q", *sys.argv[1:]], cwd=ROOT, env=env).returncode
    finally:
        # taskkill /T also removes the child of the venv launcher process
        subprocess.run(["taskkill", "/PID", str(server.pid), "/T", "/F"], capture_output=True)


if __name__ == "__main__":
    sys.exit(main())
