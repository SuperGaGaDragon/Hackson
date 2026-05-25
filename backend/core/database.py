"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from pymongo import MongoClient
from pymongo.database import Database

from core.config import get_settings

_client: MongoClient | None = None


def connect_mongo() -> None:
    """Open the process-level MongoDB client and ensure indexes."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.mongo_uri)


def close_mongo() -> None:
    """Close the process-level MongoDB client."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_database() -> Database:
    """Return the configured MongoDB database."""
    if _client is None:
        connect_mongo()
    settings = get_settings()
    assert _client is not None
    return _client[settings.mongo_database]
