from __future__ import annotations

import os
from pathlib import Path

import duckdb

_conn: duckdb.DuckDBPyConnection | None = None


def get_db_path() -> str:
    return os.environ.get("TEST_STORY_DB", str(Path.home() / ".test-story" / "data.duckdb"))


def get_db() -> duckdb.DuckDBPyConnection:
    global _conn
    if _conn is None:
        path = get_db_path()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        _conn = duckdb.connect(path)
        from story.db.schema import init_db
        init_db(_conn)
    return _conn


def close_db() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None
