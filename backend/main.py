"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from fastapi import FastAPI

from conversations.routes import idle_router, router as conversations_router
from core.database import close_mongo, connect_mongo
from interactions.routes import companion_router, idle_router as interaction_idle_router
from users.routes import router as users_router


def create_app() -> FastAPI:
    """Create the FastAPI application and register product modules."""
    app = FastAPI(title="Hackson Backend", version="0.1.0")

    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(conversations_router, prefix="/api/conversations", tags=["conversations"])
    app.include_router(idle_router, prefix="/api/idle", tags=["idle"])
    app.include_router(interaction_idle_router, prefix="/api/idle", tags=["idle-interactions"])
    app.include_router(companion_router, prefix="/api/companion", tags=["companion-interactions"])

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
