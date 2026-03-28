from __future__ import annotations

import json
from datetime import datetime

import duckdb

from story.errors import AppError
from story.models.step import Assertion, ActualRequest, Step


def _row_to_step(row: tuple, full: bool = False) -> Step:
    actual = row[6]
    if actual and isinstance(actual, str):
        actual = json.loads(actual)
    assertions = row[7]
    if assertions and isinstance(assertions, str):
        assertions = json.loads(assertions)

    return Step(
        index=row[1],
        chapter=row[2],
        description=row[3],
        narrative=row[4] if full else None,
        status=row[5],
        actual=ActualRequest(**actual) if actual and full else None,
        assertions=[Assertion(**a) for a in assertions] if assertions and full else None,
        duration_ms=row[8],
        started_at=row[9],
        finished_at=row[10],
    )


_SELECT_STEP = "SELECT run_id, idx, chapter, description, narrative, status, actual, assertions, duration_ms, started_at, finished_at FROM steps"


def insert_step(conn: duckdb.DuckDBPyConnection, run_id: str, idx: int,
                chapter: str | None = None, description: str | None = None,
                narrative: str | None = None) -> None:
    conn.execute(
        "INSERT INTO steps (run_id, idx, chapter, description, narrative, status) VALUES (?, ?, ?, ?, ?, 'pending')",
        [run_id, idx, chapter, description, narrative],
    )


def update_step(conn: duckdb.DuckDBPyConnection, run_id: str, idx: int,
                status: str | None = None, actual: dict | None = None,
                assertions: list[dict] | None = None, duration_ms: int | None = None,
                started_at: datetime | None = None, finished_at: datetime | None = None) -> None:
    sets = []
    params: list = []
    if status:
        sets.append("status = ?")
        params.append(status)
    if actual is not None:
        sets.append("actual = ?")
        params.append(json.dumps(actual))
    if assertions is not None:
        sets.append("assertions = ?")
        params.append(json.dumps(assertions))
    if duration_ms is not None:
        sets.append("duration_ms = ?")
        params.append(duration_ms)
    if started_at:
        sets.append("started_at = ?")
        params.append(started_at)
    if finished_at:
        sets.append("finished_at = ?")
        params.append(finished_at)
    if sets:
        params.extend([run_id, idx])
        conn.execute(f"UPDATE steps SET {', '.join(sets)} WHERE run_id = ? AND idx = ?", params)


def list_steps(conn: duckdb.DuckDBPyConnection, run_id: str, status: str | None = None) -> list[Step]:
    where = "WHERE run_id = ?"
    params: list = [run_id]
    if status:
        where += " AND status = ?"
        params.append(status)
    rows = conn.execute(f"{_SELECT_STEP} {where} ORDER BY idx", params).fetchall()
    return [_row_to_step(r) for r in rows]


def get_step(conn: duckdb.DuckDBPyConnection, run_id: str, idx: int) -> Step:
    row = conn.execute(f"{_SELECT_STEP} WHERE run_id = ? AND idx = ?", [run_id, idx]).fetchone()
    if not row:
        raise AppError("resource_not_found", f"Step {idx} not found in run '{run_id}'", 404)
    return _row_to_step(row, full=True)
