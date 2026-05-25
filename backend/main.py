"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from fastapi import FastAPI

from core.database import close_mongo, connect_mongo
from users.routes import router as users_router


def create_app() -> FastAPI:
    """Create the FastAPI application and register product modules."""
    app = FastAPI(title="Hackson Backend", version="0.1.0")

    app.include_router(users_router, prefix="/api/users", tags=["users"])

    @app.on_event("startup")
    def _startup() -> None:
        connect_mongo()

    @app.on_event("shutdown")
    def _shutdown() -> None:
        close_mongo()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
