from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from test_story import __version__
from test_story.db import get_db, close_db
from test_story.errors import AppError
from test_story.runner import RunExecutor
from test_story.server.sse import EventBus


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db()
    app.state.db = db
    app.state.event_bus = EventBus()
    app.state.start_time = time.time()

    config_row = db.execute("SELECT max_concurrent_runs FROM config WHERE id = 1").fetchone()
    max_concurrent = config_row[0] if config_row else 3

    executor = RunExecutor(db, app.state.event_bus, max_concurrent=max_concurrent)
    app.state.executor = executor
    executor.start()

    yield

    await executor.stop()
    close_db()


def create_app() -> FastAPI:
    app = FastAPI(title="test-story", version=__version__, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    from test_story.server.routes import server, providers, harnesses, collections, stories, runs, steps
    app.include_router(server.router)
    app.include_router(providers.router, prefix="/api/v1")
    app.include_router(harnesses.router, prefix="/api/v1")
    app.include_router(collections.router, prefix="/api/v1")
    app.include_router(stories.router, prefix="/api/v1")
    app.include_router(runs.router, prefix="/api/v1")
    app.include_router(steps.router, prefix="/api/v1")

    return app
