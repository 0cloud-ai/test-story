from __future__ import annotations

from pydantic import BaseModel


class HarnessConfig(BaseModel):
    timeout_seconds: int = 300


class HarnessUpdate(BaseModel):
    provider: str | None = None
    config: HarnessConfig | None = None


class Harness(BaseModel):
    name: str
    available: bool
    version: str | None = None
    provider: str | None = None
    config: HarnessConfig = HarnessConfig()
    reason: str | None = None
