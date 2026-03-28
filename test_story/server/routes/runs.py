from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse

import duckdb

from test_story.db.queries import runs as run_q, stories as story_q, steps as step_q
from test_story.errors import AppError
from test_story.models.common import PaginatedResponse
from test_story.models.run import Run, RunCreate
from test_story.models.story import parse_meta
from test_story.server.deps import get_db, get_executor, get_event_bus
from test_story.server.sse import EventBus, format_sse

router = APIRouter(prefix="/runs", tags=["runs"])


@router.post("", status_code=202)
async def quick_run(
    request: Request,
    story: UploadFile = File(...),
    options: str = Form("{}"),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
    executor=Depends(get_executor),
):
    content = (await story.read()).decode("utf-8")
    opts = json.loads(options) if options else {}

    collection_id = opts.get("collection_id")
    if collection_id:
        from test_story.db.queries import collections as coll_q
        coll_q.get_collection_summary(db, collection_id)
        story_obj = story_q.create_story(db, collection_id, content)
    else:
        meta = parse_meta(content)
        from test_story.ids import gen_id
        from datetime import datetime, timezone
        sid = gen_id("story")
        now = datetime.now(timezone.utc)
        db.execute(
            "INSERT INTO stories (id, collection_id, title, scene, target, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [sid, None, meta.title, meta.scene, meta.target, content, now, now],
        )
        story_obj = story_q.get_story(db, sid)

    config_row = db.execute("SELECT harness FROM config WHERE id = 1").fetchone()
    default_harness = config_row[0] if config_row else "claude-code"

    harness = opts.get("harness") or default_harness
    target = opts.get("target") or story_obj.target
    env = opts.get("env")

    run = run_q.create_run(db, story_obj.id, harness, target=target, env=env)
    await executor.submit(run.id)

    return {
        "story": {"id": story_obj.id, "title": story_obj.title},
        "run": {"id": run.id, "status": "queued", "created_at": str(run.created_at)},
    }


@router.post("/{run_id}/retry", status_code=202, response_model=Run)
async def retry_run(run_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db), executor=Depends(get_executor)):
    old_run = run_q.get_run(db, run_id)
    new_run = run_q.create_run(db, old_run.story_id, old_run.harness, target=old_run.target, env=old_run.env)
    await executor.submit(new_run.id)
    return new_run


@router.get("", response_model=PaginatedResponse[Run])
def list_runs(story_id: str | None = None, collection_id: str | None = None,
              batch_id: str | None = None, status: str | None = None,
              page: int = 1, per_page: int = 20,
              db: duckdb.DuckDBPyConnection = Depends(get_db)):
    items, total = run_q.list_runs(db, story_id=story_id, collection_id=collection_id,
                                    batch_id=batch_id, status=status, page=page, per_page=per_page)
    return PaginatedResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/{run_id}", response_model=Run)
def get_run(run_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    run = run_q.get_run(db, run_id)
    steps = step_q.list_steps(db, run_id)
    run.steps = steps
    return run


@router.get("/{run_id}/stream")
async def stream_run(run_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db),
                     event_bus: EventBus = Depends(get_event_bus)):
    run = run_q.get_run(db, run_id)
    if run.status in ("passed", "failed", "error", "cancelled"):
        raise AppError("conflict", "Run has already finished", 409)

    q = event_bus.subscribe(run_id)

    async def generate():
        try:
            while True:
                msg = await q.get()
                if msg is None:
                    break
                yield format_sse(msg.event, msg.data)
        finally:
            event_bus.unsubscribe(run_id, q)

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/{run_id}/cancel")
def cancel_run(run_id: str, request: Request, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    run = run_q.get_run(db, run_id)
    if run.status in ("passed", "failed", "error", "cancelled"):
        raise AppError("conflict", "Run has already finished", 409)
    request.app.state.executor.cancel(run_id)
    return {"id": run_id, "status": "cancelled"}
