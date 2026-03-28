from __future__ import annotations

from fastapi import APIRouter, Depends

import duckdb

from test_story.db.queries import steps as step_q
from test_story.models.step import Step
from test_story.server.deps import get_db

router = APIRouter(prefix="/runs/{run_id}/steps", tags=["steps"])


@router.get("", response_model=list[Step])
def list_steps(run_id: str, status: str | None = None, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return step_q.list_steps(db, run_id, status=status)


@router.get("/{step_index}", response_model=Step)
def get_step(run_id: str, step_index: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return step_q.get_step(db, run_id, step_index)
