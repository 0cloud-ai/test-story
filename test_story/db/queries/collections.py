from __future__ import annotations

from datetime import datetime, timezone

import duckdb

from test_story.errors import AppError
from test_story.ids import gen_id
from test_story.models.collection import Collection, CollectionCreate, CollectionSummary, CollectionUpdate, StorySummary


def _row_to_summary(row: tuple) -> CollectionSummary:
    return CollectionSummary(
        id=row[0], name=row[1], description=row[2], target=row[3],
        harness=row[4], story_count=row[5], created_at=row[6], updated_at=row[7],
    )


def create_collection(conn: duckdb.DuckDBPyConnection, data: CollectionCreate) -> CollectionSummary:
    existing = conn.execute("SELECT id FROM collections WHERE name = ?", [data.name]).fetchone()
    if existing:
        raise AppError("conflict", f"Collection '{data.name}' already exists", 409)

    cid = gen_id("coll")
    now = datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO collections (id, name, description, target, harness, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [cid, data.name, data.description, data.target, data.harness, now, now],
    )
    return get_collection_summary(conn, cid)


def list_collections(conn: duckdb.DuckDBPyConnection, page: int = 1, per_page: int = 20) -> tuple[list[CollectionSummary], int]:
    total = conn.execute("SELECT count(*) FROM collections").fetchone()[0]
    rows = conn.execute(
        """SELECT c.id, c.name, c.description, c.target, c.harness,
                  (SELECT count(*) FROM stories s WHERE s.collection_id = c.id),
                  c.created_at, c.updated_at
           FROM collections c ORDER BY c.created_at DESC LIMIT ? OFFSET ?""",
        [per_page, (page - 1) * per_page],
    ).fetchall()
    return [_row_to_summary(r) for r in rows], total


def get_collection_summary(conn: duckdb.DuckDBPyConnection, id_or_name: str) -> CollectionSummary:
    row = conn.execute(
        """SELECT c.id, c.name, c.description, c.target, c.harness,
                  (SELECT count(*) FROM stories s WHERE s.collection_id = c.id),
                  c.created_at, c.updated_at
           FROM collections c WHERE c.id = ? OR c.name = ?""",
        [id_or_name, id_or_name],
    ).fetchone()
    if not row:
        raise AppError("resource_not_found", f"Collection '{id_or_name}' not found", 404)
    return _row_to_summary(row)


def get_collection(conn: duckdb.DuckDBPyConnection, id_or_name: str) -> Collection:
    summary = get_collection_summary(conn, id_or_name)
    story_rows = conn.execute(
        "SELECT id, title, scene FROM stories WHERE collection_id = ? ORDER BY created_at",
        [summary.id],
    ).fetchall()
    stories = [StorySummary(id=r[0], title=r[1], scene=r[2]) for r in story_rows]
    return Collection(**summary.model_dump(), stories=stories)


def update_collection(conn: duckdb.DuckDBPyConnection, id_or_name: str, data: CollectionUpdate) -> CollectionSummary:
    coll = get_collection_summary(conn, id_or_name)
    now = datetime.now(timezone.utc)
    updates = []
    params = []
    for field in ["name", "description", "target", "harness"]:
        val = getattr(data, field)
        if val is not None:
            updates.append(f"{field} = ?")
            params.append(val)
    if updates:
        updates.append("updated_at = ?")
        params.append(now)
        params.append(coll.id)
        conn.execute(f"UPDATE collections SET {', '.join(updates)} WHERE id = ?", params)
    return get_collection_summary(conn, coll.id)


def delete_collection(conn: duckdb.DuckDBPyConnection, id_or_name: str, cascade: bool = False) -> None:
    coll = get_collection_summary(conn, id_or_name)
    if not cascade and coll.story_count > 0:
        raise AppError("conflict", f"Collection has {coll.story_count} stories. Use cascade=true to delete.", 409)
    if cascade:
        story_ids = [r[0] for r in conn.execute("SELECT id FROM stories WHERE collection_id = ?", [coll.id]).fetchall()]
        for sid in story_ids:
            conn.execute("DELETE FROM steps WHERE run_id IN (SELECT id FROM runs WHERE story_id = ?)", [sid])
            conn.execute("DELETE FROM runs WHERE story_id = ?", [sid])
        conn.execute("DELETE FROM stories WHERE collection_id = ?", [coll.id])
    conn.execute("DELETE FROM collections WHERE id = ?", [coll.id])
