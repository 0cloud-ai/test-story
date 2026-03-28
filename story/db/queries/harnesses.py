from __future__ import annotations

import json
import shutil

import duckdb

from story.errors import AppError
from story.models.harness import Harness, HarnessConfig, HarnessUpdate

VERSION_COMMANDS = {
    "claude-code": "claude --version",
    "claude-agent-sdk": "claude --version",
    "opencode": "opencode --version",
}

BINARY_NAMES = {
    "claude-code": "claude",
    "claude-agent-sdk": "claude",
    "opencode": "opencode",
}


def _detect_availability(name: str) -> tuple[bool, str | None, str | None]:
    binary = BINARY_NAMES.get(name)
    if not binary:
        return False, None, f"Unknown harness '{name}'"
    available = shutil.which(binary) is not None
    if not available:
        return False, None, f"'{binary}' not found in PATH"
    return True, None, None


def _row_to_harness(row: tuple) -> Harness:
    name = row[0]
    provider_name = row[1]
    cfg = row[2] if isinstance(row[2], dict) else json.loads(row[2])
    available, version, reason = _detect_availability(name)
    return Harness(
        name=name,
        available=available,
        version=version,
        provider=provider_name,
        config=HarnessConfig(**cfg),
        reason=reason,
    )


def list_harnesses(conn: duckdb.DuckDBPyConnection) -> list[Harness]:
    rows = conn.execute("SELECT name, provider_name, config FROM harnesses ORDER BY name").fetchall()
    return [_row_to_harness(r) for r in rows]


def get_harness(conn: duckdb.DuckDBPyConnection, name: str) -> Harness:
    row = conn.execute("SELECT name, provider_name, config FROM harnesses WHERE name = ?", [name]).fetchone()
    if not row:
        raise AppError("resource_not_found", f"Harness '{name}' not found", 404)
    return _row_to_harness(row)


def update_harness(conn: duckdb.DuckDBPyConnection, name: str, data: HarnessUpdate) -> Harness:
    harness = get_harness(conn, name)
    if data.provider is not None:
        from story.db.queries.providers import get_provider
        get_provider(conn, data.provider)
        conn.execute("UPDATE harnesses SET provider_name = ? WHERE name = ?", [data.provider, name])

    if data.config is not None:
        merged = harness.config.model_dump()
        merged.update({k: v for k, v in data.config.model_dump().items() if v is not None})
        conn.execute("UPDATE harnesses SET config = ? WHERE name = ?", [json.dumps(merged), name])

    return get_harness(conn, name)
