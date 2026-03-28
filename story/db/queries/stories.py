from __future__ import annotations

from datetime import datetime, timezone

import duckdb

from story.errors import AppError
from story.ids import gen_id
from story.models.story import Story, parse_meta


def _row_to_story(row: tuple, include_content: bool = False) -> Story:
    return Story(
        id=row[0], collection_id=row[1], title=row[2], scene=row[3],
        target=row[4], content=row[5] if include_content else None,
        created_at=row[6], updated_at=row[7],
    )


def create_story(conn: duckdb.DuckDBPyConnection, collection_id: str, content: str) -> Story:
    from story.db.queries.collections import get_collection_summary
    get_collection_summary(conn, collection_id)

    meta = parse_meta(content)
    if not meta.scene:
        raise AppError("unprocessable", "Story is missing 'scene' in meta block", 422)

    sid = gen_id("story")
    now = datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO stories (id, collection_id, title, scene, target, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [sid, collection_id, meta.title, meta.scene, meta.target, content, now, now],
    )
    return get_story(conn, sid)


def list_stories(conn: duckdb.DuckDBPyConnection, collection_id: str, scene: str | None = None, page: int = 1, per_page: int = 20) -> tuple[list[Story], int]:
    from story.db.queries.collections import get_collection_summary
    coll = get_collection_summary(conn, collection_id)

    where = "WHERE collection_id = ?"
    params: list = [coll.id]
    if scene:
        where += " AND scene = ?"
        params.append(scene)

    total = conn.execute(f"SELECT count(*) FROM stories {where}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT id, collection_id, title, scene, target, content, created_at, updated_at FROM stories {where} ORDER BY created_at LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page],
    ).fetchall()
    return [_row_to_story(r) for r in rows], total


def get_story(conn: duckdb.DuckDBPyConnection, story_id: str, include_content: bool = True) -> Story:
    row = conn.execute(
        "SELECT id, collection_id, title, scene, target, content, created_at, updated_at FROM stories WHERE id = ?",
        [story_id],
    ).fetchone()
    if not row:
        raise AppError("resource_not_found", f"Story '{story_id}' not found", 404)
    return _row_to_story(row, include_content=include_content)


def update_story(conn: duckdb.DuckDBPyConnection, story_id: str, content: str) -> Story:
    get_story(conn, story_id)
    meta = parse_meta(content)
    now = datetime.now(timezone.utc)
    conn.execute(
        "UPDATE stories SET title = ?, scene = ?, target = ?, content = ?, updated_at = ? WHERE id = ?",
        [meta.title, meta.scene, meta.target, content, now, story_id],
    )
    return get_story(conn, story_id)


def delete_story(conn: duckdb.DuckDBPyConnection, story_id: str, cascade: bool = False) -> None:
    get_story(conn, story_id)
    if cascade:
        conn.execute("DELETE FROM steps WHERE run_id IN (SELECT id FROM runs WHERE story_id = ?)", [story_id])
        conn.execute("DELETE FROM runs WHERE story_id = ?", [story_id])
    else:
        has_runs = conn.execute("SELECT count(*) FROM runs WHERE story_id = ?", [story_id]).fetchone()[0]
        if has_runs > 0:
            raise AppError("conflict", f"Story has {has_runs} runs. Use cascade=true to delete.", 409)
    conn.execute("DELETE FROM stories WHERE id = ?", [story_id])
