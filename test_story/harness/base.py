from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class StepStarted:
    index: int
    chapter: str | None = None
    description: str | None = None
    narrative: str | None = None


@dataclass
class StepCompleted:
    index: int
    status: str = "passed"
    actual: dict | None = None
    assertions: list[dict] | None = None
    duration_ms: int = 0


@dataclass
class StepLog:
    index: int
    message: str = ""


@dataclass
class RunError:
    message: str = ""


StepEvent = StepStarted | StepCompleted | StepLog | RunError


def extract_chapters(markdown: str) -> list[tuple[str, str]]:
    """Extract (chapter_title, chapter_body) from H2 headings."""
    parts = re.split(r"^## ", markdown, flags=re.MULTILINE)
    chapters = []
    for part in parts[1:]:
        lines = part.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        if title.startswith("楔子") or title.startswith("尾声"):
            continue
        chapters.append((title, body))
    return chapters


class AbstractHarness:
    name: str = ""

    async def execute(self, story_content: str, target: str, env: dict | None = None) -> AsyncIterator[StepEvent]:
        raise NotImplementedError
        yield  # make it an async generator
