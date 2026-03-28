from __future__ import annotations

import json
from datetime import datetime, timezone

import duckdb

from test_story.errors import AppError
from test_story.ids import gen_id
from test_story.models.run import Run, RunStatus, StepSummary


def _row_to_run(row: tuple, include_steps: bool = False) -> Run:
    step_summary = row[7]
    if step_summary and isinstance(step_summary, str):
        step_summary = json.loads(step_summary)
    if step_summary and isinstance(step_summary, dict):
        step_summary = StepSummary(**step_summary)

    env = row[6]
    if env and isinstance(env, str):
        env = json.loads(env)

    return Run(
        id=row[0], story_id=row[1], batch_id=row[2], status=row[3],
        harness=row[4], target=row[5], env=env, step_summary=step_summary,
        story_title=row[8] if len(row) > 8 else None,
        created_at=row[9] if len(row) > 9 else row[8] if len(row) > 8 else None,
        started_at=row[10] if len(row) > 10 else None,
        finished_at=row[11] if len(row) > 11 else None,
        duration_ms=row[12] if len(row) > 12 else None,
    )


_SELECT_RUN = """
    SELECT r.id, r.story_id, r.batch_id, r.status, r.harness, r.target, r.env,
           r.step_summary, s.title, r.created_at, r.started_at, r.finished_at, r.duration_ms
    FROM runs r LEFT JOIN stories s ON r.story_id = s.id
"""


def create_run(conn: duckdb.DuckDBPyConnection, story_id: str, harness: str,
               target: str | None = None, env: dict | None = None,
               batch_id: str | None = None) -> Run:
    rid = gen_id("run")
    now = datetime.now(timezone.utc)
    conn.execute(
        "INSERT INTO runs (id, story_id, batch_id, status, harness, target, env, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [rid, story_id, batch_id, "queued", harness, target, json.dumps(env) if env else None, now],
    )
    return get_run(conn, rid)


def list_runs(conn: duckdb.DuckDBPyConnection, story_id: str | None = None,
              collection_id: str | None = None, batch_id: str | None = None,
              status: str | None = None, page: int = 1, per_page: int = 20) -> tuple[list[Run], int]:
    where_parts = []
    params: list = []

    if story_id:
        where_parts.append("r.story_id = ?")
        params.append(story_id)
    if collection_id:
        where_parts.append("s.collection_id = ?")
        params.append(collection_id)
    if batch_id:
        where_parts.append("r.batch_id = ?")
        params.append(batch_id)
    if status:
        where_parts.append("r.status = ?")
        params.append(status)

    where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""

    total = conn.execute(
        f"SELECT count(*) FROM runs r LEFT JOIN stories s ON r.story_id = s.id {where}", params
    ).fetchone()[0]
    rows = conn.execute(
        f"{_SELECT_RUN} {where} ORDER BY r.created_at DESC LIMIT ? OFFSET ?",
        params + [per_page, (page - 1) * per_page],
    ).fetchall()
    return [_row_to_run(r) for r in rows], total


def get_run(conn: duckdb.DuckDBPyConnection, run_id: str) -> Run:
    row = conn.execute(f"{_SELECT_RUN} WHERE r.id = ?", [run_id]).fetchone()
    if not row:
        raise AppError("resource_not_found", f"Run '{run_id}' not found", 404)
    return _row_to_run(row)


def update_run_status(conn: duckdb.DuckDBPyConnection, run_id: str, status: str,
                      started_at: datetime | None = None, finished_at: datetime | None = None,
                      duration_ms: int | None = None, step_summary: dict | None = None) -> None:
    sets = ["status = ?"]
    params: list = [status]
    if started_at:
        sets.append("started_at = ?")
        params.append(started_at)
    if finished_at:
        sets.append("finished_at = ?")
        params.append(finished_at)
    if duration_ms is not None:
        sets.append("duration_ms = ?")
        params.append(duration_ms)
    if step_summary is not None:
        sets.append("step_summary = ?")
        params.append(json.dumps(step_summary))
    params.append(run_id)
    conn.execute(f"UPDATE runs SET {', '.join(sets)} WHERE id = ?", params)
