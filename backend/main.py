"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from agents.routes import router as agents_router
from conversations.routes import idle_router, router as conversations_router
from core.config import get_settings
from core.database import close_mongo, connect_mongo
from interactions.routes import companion_router, idle_router as interaction_idle_router
from tasks.routes import router as tasks_router
from users.routes import router as users_router
from work_mode.routes import router as work_mode_router


def create_app() -> FastAPI:
    """Create the FastAPI application and register product modules."""
    app = FastAPI(title="Hackson Backend", version="0.1.0")

    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
    app.include_router(conversations_router, prefix="/api/conversations", tags=["conversations"])
    app.include_router(idle_router, prefix="/api/idle", tags=["idle"])
    app.include_router(interaction_idle_router, prefix="/api/idle", tags=["idle-interactions"])
    app.include_router(companion_router, prefix="/api/companion", tags=["companion-interactions"])
    app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks"])
    app.include_router(work_mode_router, prefix="/api/work", tags=["work-mode"])

    @app.on_event("startup")
    def _startup() -> None:
        connect_mongo()

    @app.on_event("shutdown")
    def _shutdown() -> None:
        close_mongo()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    _mount_static_frontend(app)
    return app


def _mount_static_frontend(app: FastAPI) -> None:
    """Serve the built React app from the backend in production."""
    static_frontend_dir = get_settings().static_frontend_dir
    if not static_frontend_dir:
        return

    frontend_dir = Path(static_frontend_dir)
    index_file = frontend_dir / "index.html"
    assets_dir = frontend_dir / "assets"
    if not index_file.is_file():
        raise RuntimeError(f"static_frontend_index_missing:{index_file}")
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    def frontend_index() -> FileResponse:
        return FileResponse(index_file)

    @app.get("/{path:path}", include_in_schema=False)
    def frontend_fallback(path: str) -> FileResponse:
        return FileResponse(index_file)


app = create_app()
