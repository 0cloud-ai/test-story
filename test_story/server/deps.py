from __future__ import annotations

from fastapi import Request

import duckdb

from test_story.runner import RunExecutor
from test_story.server.sse import EventBus


def get_db(request: Request) -> duckdb.DuckDBPyConnection:
    return request.app.state.db


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def get_executor(request: Request) -> RunExecutor:
    return request.app.state.executor
