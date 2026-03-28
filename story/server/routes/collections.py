from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

import duckdb

from story.db.queries import collections as coll_q, stories as story_q, runs as run_q
from story.ids import gen_id
from story.models.collection import Collection, CollectionCreate, CollectionSummary, CollectionUpdate, BatchRun
from story.models.common import PaginatedResponse
from story.server.deps import get_db, get_executor

router = APIRouter(prefix="/collections", tags=["collections"])


@router.post("", status_code=201, response_model=CollectionSummary)
def create_collection(data: CollectionCreate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return coll_q.create_collection(db, data)


@router.get("", response_model=PaginatedResponse[CollectionSummary])
def list_collections(page: int = 1, per_page: int = 20, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    items, total = coll_q.list_collections(db, page=page, per_page=per_page)
    return PaginatedResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/{collection_id}", response_model=Collection)
def get_collection(collection_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return coll_q.get_collection(db, collection_id)


@router.patch("/{collection_id}", response_model=CollectionSummary)
def update_collection(collection_id: str, data: CollectionUpdate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return coll_q.update_collection(db, collection_id, data)


@router.delete("/{collection_id}", status_code=204)
def delete_collection(collection_id: str, cascade: bool = False, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    coll_q.delete_collection(db, collection_id, cascade=cascade)


@router.post("/{collection_id}/runs", status_code=202, response_model=BatchRun)
async def run_collection(collection_id: str, target: str | None = None, harness: str | None = None,
                         db: duckdb.DuckDBPyConnection = Depends(get_db),
                         executor=Depends(get_executor)):
    coll = coll_q.get_collection(db, collection_id)
    if not coll.stories:
        from story.errors import AppError
        raise AppError("conflict", "Collection has no stories to execute", 409)

    config_row = db.execute("SELECT harness FROM config WHERE id = 1").fetchone()
    default_harness = config_row[0] if config_row else "claude-code"

    batch_id = gen_id("batch")
    runs_list = []
    for s in coll.stories:
        story = story_q.get_story(db, s.id)
        h = harness or coll.harness or default_harness
        t = target or story.target or coll.target
        run = run_q.create_run(db, s.id, h, target=t, batch_id=batch_id)
        runs_list.append({"id": run.id, "story_id": s.id, "story_title": s.title, "status": "queued"})
        await executor.submit(run.id)

    return BatchRun(
        batch_id=batch_id,
        collection_id=coll.id,
        status="queued",
        runs=runs_list,
        total_stories=len(coll.stories),
        created_at=datetime.now(timezone.utc),
    )
