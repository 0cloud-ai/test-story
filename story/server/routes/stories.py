from __future__ import annotations

from fastapi import APIRouter, Depends, Request

import duckdb

from story.db.queries import stories as story_q, runs as run_q
from story.models.common import PaginatedResponse
from story.models.run import Run, RunCreate
from story.models.story import Story
from story.server.deps import get_db, get_executor

router = APIRouter(tags=["stories"])


@router.post("/collections/{collection_id}/stories", status_code=201, response_model=Story)
async def create_story(collection_id: str, request: Request, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    body = await request.body()
    content = body.decode("utf-8")
    story = story_q.create_story(db, collection_id, content)
    story.content = None
    return story


@router.get("/collections/{collection_id}/stories", response_model=PaginatedResponse[Story])
def list_stories(collection_id: str, scene: str | None = None, page: int = 1, per_page: int = 20,
                 db: duckdb.DuckDBPyConnection = Depends(get_db)):
    items, total = story_q.list_stories(db, collection_id, scene=scene, page=page, per_page=per_page)
    return PaginatedResponse(items=items, total=total, page=page, per_page=per_page)


@router.get("/stories/{story_id}", response_model=Story)
def get_story(story_id: str, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    return story_q.get_story(db, story_id)


@router.put("/stories/{story_id}", response_model=Story)
async def update_story(story_id: str, request: Request, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    body = await request.body()
    content = body.decode("utf-8")
    story = story_q.update_story(db, story_id, content)
    story.content = None
    return story


@router.post("/stories/{story_id}/runs", status_code=202, response_model=Run)
async def run_story(story_id: str, data: RunCreate | None = None,
                    db: duckdb.DuckDBPyConnection = Depends(get_db),
                    executor=Depends(get_executor)):
    story = story_q.get_story(db, story_id)
    config_row = db.execute("SELECT harness FROM config WHERE id = 1").fetchone()
    default_harness = config_row[0] if config_row else "claude-code"

    harness = (data.harness if data else None) or default_harness
    target = (data.target if data else None) or story.target
    env = data.env if data else None

    run = run_q.create_run(db, story.id, harness, target=target, env=env)
    await executor.submit(run.id)
    return run


@router.delete("/stories/{story_id}", status_code=204)
def delete_story(story_id: str, cascade: bool = False, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    story_q.delete_story(db, story_id, cascade=cascade)
