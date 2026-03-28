from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CollectionCreate(BaseModel):
    name: str
    description: str | None = None
    target: str | None = None
    harness: str | None = None


class CollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target: str | None = None
    harness: str | None = None


class CollectionSummary(BaseModel):
    id: str
    name: str
    description: str | None = None
    target: str | None = None
    harness: str | None = None
    story_count: int = 0
    created_at: datetime
    updated_at: datetime


class StorySummary(BaseModel):
    id: str
    title: str
    scene: str


class Collection(CollectionSummary):
    stories: list[StorySummary] = []


class BatchRun(BaseModel):
    batch_id: str
    collection_id: str
    status: str = "queued"
    runs: list[dict]
    total_stories: int
    created_at: datetime
