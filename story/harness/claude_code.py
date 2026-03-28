from __future__ import annotations

import asyncio
import re
from typing import AsyncIterator

from story.harness.base import (
    AbstractHarness, StepEvent, StepStarted, StepCompleted, StepLog,
    extract_chapters,
)


class ClaudeCodeHarness(AbstractHarness):
    name = "claude-code"

    async def execute(self, story_content: str, target: str, env: dict | None = None) -> AsyncIterator[StepEvent]:
        chapters = extract_chapters(story_content)
        step_idx = 0

        for chapter_title, chapter_body in chapters:
            paragraphs = [p.strip() for p in chapter_body.split("\n\n") if p.strip()]
            for para in paragraphs:
                if len(para) < 20:
                    continue
                step_idx += 1
                desc = para[:60].replace("\n", " ")
                if len(para) > 60:
                    desc += "..."

                yield StepStarted(
                    index=step_idx,
                    chapter=chapter_title,
                    description=desc,
                    narrative=para,
                )

                yield StepLog(index=step_idx, message=f"[stub] Simulating test for: {desc}")

                await asyncio.sleep(0.2)

                yield StepCompleted(
                    index=step_idx,
                    status="passed",
                    actual={"method": "STUB", "url": target, "status_code": 200, "body_summary": "Stub response"},
                    assertions=[{"description": desc, "passed": True}],
                    duration_ms=200,
                )
