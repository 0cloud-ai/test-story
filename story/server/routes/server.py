from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

import duckdb

from story import __version__
from story.server.deps import get_db

router = APIRouter()


@router.get("/healthz")
def healthz(request: Request):
    uptime = time.time() - getattr(request.app.state, "start_time", time.time())
    return {"status": "ok", "version": __version__, "uptime_seconds": int(uptime)}


class ConfigResponse(BaseModel):
    harness: str | None = None
    provider: str | None = None
    supported_scenes: list[str] = ["api"]
    max_concurrent_runs: int = 3


class ConfigUpdate(BaseModel):
    harness: str | None = None
    provider: str | None = None
    max_concurrent_runs: int | None = None


@router.get("/api/v1/config", response_model=ConfigResponse)
def get_config(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    row = db.execute("SELECT harness, provider, supported_scenes, max_concurrent_runs FROM config WHERE id = 1").fetchone()
    scenes = row[2]
    if isinstance(scenes, str):
        scenes = json.loads(scenes)
    return ConfigResponse(harness=row[0], provider=row[1], supported_scenes=scenes, max_concurrent_runs=row[3])


@router.patch("/api/v1/config", response_model=ConfigResponse)
def update_config(data: ConfigUpdate, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    sets = []
    params: list = []
    if data.harness is not None:
        sets.append("harness = ?")
        params.append(data.harness)
    if data.provider is not None:
        sets.append("provider = ?")
        params.append(data.provider)
    if data.max_concurrent_runs is not None:
        sets.append("max_concurrent_runs = ?")
        params.append(data.max_concurrent_runs)
    if sets:
        params.append(1)
        db.execute(f"UPDATE config SET {', '.join(sets)} WHERE id = ?", params)
    return get_config(db)
