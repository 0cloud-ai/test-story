from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb

from test_story.errors import AppError
from test_story.ids import gen_id
from test_story.models.provider import Provider, ProviderConfig, ProviderCreate, ProviderUpdate


def _row_to_provider(row: tuple) -> Provider:
    cfg = row[3] if isinstance(row[3], dict) else json.loads(row[3])
    return Provider(
        id=row[0],
        name=row[1],
        type=row[2],
        config=ProviderConfig(**cfg),
        created_at=row[4],
        updated_at=row[5],
    )


def create_provider(conn: duckdb.DuckDBPyConnection, data: ProviderCreate) -> Provider:
    existing = conn.execute("SELECT id FROM providers WHERE name = ?", [data.name]).fetchone()
    if existing:
        raise AppError("conflict", f"Provider '{data.name}' already exists", 409)

    pid = gen_id("prov")
    now = datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO providers (id, name, type, config, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        [pid, data.name, data.type, json.dumps(data.config.model_dump()), now, now],
    )
    return get_provider(conn, pid)


def list_providers(conn: duckdb.DuckDBPyConnection, type_filter: str | None = None, page: int = 1, per_page: int = 20) -> tuple[list[Provider], int]:
    where = ""
    params: list = []
    if type_filter:
        where = "WHERE type = ?"
        params.append(type_filter)

    total = conn.execute(f"SELECT count(*) FROM providers {where}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT id, name, type, config, created_at, updated_at FROM providers {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page],
    ).fetchall()
    return [_row_to_provider(r) for r in rows], total


def get_provider(conn: duckdb.DuckDBPyConnection, id_or_name: str) -> Provider:
    row = conn.execute(
        "SELECT id, name, type, config, created_at, updated_at FROM providers WHERE id = ? OR name = ?",
        [id_or_name, id_or_name],
    ).fetchone()
    if not row:
        raise AppError("resource_not_found", f"Provider '{id_or_name}' not found", 404)
    return _row_to_provider(row)


def update_provider(conn: duckdb.DuckDBPyConnection, id_or_name: str, data: ProviderUpdate) -> Provider:
    prov = get_provider(conn, id_or_name)
    now = datetime.now(timezone.utc)
    if data.config:
        merged = prov.config.model_dump()
        merged.update({k: v for k, v in data.config.model_dump().items() if v is not None})
        conn.execute(
            "UPDATE providers SET config = ?, updated_at = ? WHERE id = ?",
            [json.dumps(merged), now, prov.id],
        )
    return get_provider(conn, prov.id)


def delete_provider(conn: duckdb.DuckDBPyConnection, id_or_name: str) -> None:
    prov = get_provider(conn, id_or_name)
    ref = conn.execute("SELECT name FROM harnesses WHERE provider_name = ?", [prov.name]).fetchone()
    if ref:
        raise AppError("conflict", f"Provider '{prov.name}' is in use by harness '{ref[0]}'", 409)
    conn.execute("DELETE FROM providers WHERE id = ?", [prov.id])
