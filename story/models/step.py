from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class Assertion(BaseModel):
    description: str
    expected: str | None = None
    actual: str | None = None
    passed: bool = True


class ActualRequest(BaseModel):
    method: str | None = None
    url: str | None = None
    request_body: dict | None = None
    status_code: int | None = None
    response_body: dict | None = None
    body_summary: str | None = None


class Step(BaseModel):
    index: int
    chapter: str | None = None
    description: str | None = None
    narrative: str | None = None
    status: str = "pending"
    actual: ActualRequest | None = None
    assertions: list[Assertion] | None = None
    duration_ms: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
