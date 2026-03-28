from __future__ import annotations

from fastapi import APIRouter, Depends

import duckdb

from test_story.db.queries import harnesses as h_q
from test_story.models.harness import Harness, HarnessUpdate
from test_story.server.deps import get_db

router = APIRouter(prefix="/harnesses", tags=["harnesses"])


@router.get("", response_model=list[Harness])
def list_harnesses(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return h_q.list_harnesses(db)


@router.get("/{harness_name}", response_model=Harness)
def get_harness(harness_name: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return h_q.get_harness(db, harness_name)


@router.patch("/{harness_name}", response_model=Harness)
def update_harness(harness_name: str, data: HarnessUpdate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return h_q.update_harness(db, harness_name, data)
