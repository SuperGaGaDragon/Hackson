"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from __future__ import annotations

import os
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
SCREENSHOT = ROOT / "scripts" / "artifacts" / "work_mode_v1_browser_smoke.png"
BACKEND_PORT = int(os.getenv("HACKSON_SMOKE_BACKEND_PORT", "9127"))
FRONTEND_PORT = int(os.getenv("HACKSON_SMOKE_FRONTEND_PORT", "5127"))


def main() -> None:
    backend = _start(
        [
            "python",
            "-m",
            "uvicorn",
            "scripts.work_mode_v1_smoke_server:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(BACKEND_PORT),
        ],
        ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "backend")},
    )
    frontend = _start(
        [
            "npm",
            "--prefix",
            "frontend",
            "run",
            "dev",
            "--",
            "--port",
            str(FRONTEND_PORT),
            "--strictPort",
        ],
        ROOT,
        env={**os.environ, "VITE_API_BASE_URL": f"http://127.0.0.1:{BACKEND_PORT}"},
    )
    try:
        _wait_for(f"http://127.0.0.1:{BACKEND_PORT}/health")
        _wait_for(f"http://127.0.0.1:{FRONTEND_PORT}")
        subprocess.run(
            ["node", "smoke/work_mode_v1_browser_smoke.mjs"],
            cwd=FRONTEND,
            check=True,
            env={
                **os.environ,
                "HACKSON_SMOKE_FRONTEND_URL": f"http://127.0.0.1:{FRONTEND_PORT}",
                "HACKSON_SMOKE_SCREENSHOT": str(SCREENSHOT),
            },
        )
    finally:
        _stop(frontend)
        _stop(backend)


def _start(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(command, cwd=cwd, env=env, start_new_session=True)


def _stop(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    os.killpg(process.pid, signal.SIGTERM)
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=8)


def _wait_for(url: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception:
            time.sleep(0.3)
    raise RuntimeError(f"server_not_ready:{url}")


if __name__ == "__main__":
    main()
