from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class RunStatus(str, Enum):
    queued = "queued"
    running = "running"
    passed = "passed"
    failed = "failed"
    error = "error"
    cancelled = "cancelled"


class StepSummary(BaseModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    running: int = 0
    pending: int = 0
    error: int = 0


class RunCreate(BaseModel):
    target: str | None = None
    harness: str | None = None
    env: dict | None = None


class Run(BaseModel):
    id: str
    story_id: str
    story_title: str | None = None
    batch_id: str | None = None
    status: str = "queued"
    harness: str = ""
    target: str | None = None
    env: dict | None = None
    step_summary: StepSummary | None = None
    steps: list | None = None
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_ms: int | None = None
