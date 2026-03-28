from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone

import duckdb

from story.db.queries import runs as run_q, steps as step_q, stories as story_q
from story.harness import get_harness_impl
from story.harness.base import StepStarted, StepCompleted, StepLog, RunError
from story.server.sse import EventBus


class RunExecutor:
    def __init__(self, db: duckdb.DuckDBPyConnection, event_bus: EventBus, max_concurrent: int = 3):
        self._db = db
        self._event_bus = event_bus
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._task: asyncio.Task | None = None
        self._cancelled: set[str] = set()

    def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def submit(self, run_id: str) -> None:
        await self._queue.put(run_id)

    def cancel(self, run_id: str) -> None:
        self._cancelled.add(run_id)

    async def _loop(self) -> None:
        while True:
            run_id = await self._queue.get()
            asyncio.create_task(self._execute(run_id))

    async def _execute(self, run_id: str) -> None:
        async with self._semaphore:
            db = self._db
            bus = self._event_bus

            try:
                run = run_q.get_run(db, run_id)
                story = story_q.get_story(db, run.story_id)
                target = run.target or ""

                now = datetime.now(timezone.utc)
                run_q.update_run_status(db, run_id, "running", started_at=now)
                await bus.publish(run_id, "run.started", {"run_id": run_id, "status": "running"})

                harness_impl = get_harness_impl(run.harness)
                t0 = time.monotonic()

                summary = {"total": 0, "passed": 0, "failed": 0, "running": 0, "pending": 0, "error": 0}

                async for event in harness_impl.execute(story.content or "", target, run.env):
                    if run_id in self._cancelled:
                        run_q.update_run_status(db, run_id, "cancelled", finished_at=datetime.now(timezone.utc))
                        await bus.publish(run_id, "run.completed", {"run_id": run_id, "status": "cancelled"})
                        await bus.close(run_id)
                        self._cancelled.discard(run_id)
                        return

                    if isinstance(event, StepStarted):
                        step_q.insert_step(db, run_id, event.index, event.chapter, event.description, event.narrative)
                        step_q.update_step(db, run_id, event.index, status="running", started_at=datetime.now(timezone.utc))
                        summary["total"] += 1
                        summary["running"] += 1
                        await bus.publish(run_id, "step.started", {
                            "index": event.index, "chapter": event.chapter, "description": event.description,
                        })

                    elif isinstance(event, StepCompleted):
                        step_q.update_step(
                            db, run_id, event.index,
                            status=event.status,
                            actual=event.actual,
                            assertions=event.assertions,
                            duration_ms=event.duration_ms,
                            finished_at=datetime.now(timezone.utc),
                        )
                        summary["running"] = max(0, summary["running"] - 1)
                        summary[event.status] = summary.get(event.status, 0) + 1
                        run_q.update_run_status(db, run_id, "running", step_summary=summary)
                        await bus.publish(run_id, "step.completed", {
                            "index": event.index, "status": event.status, "duration_ms": event.duration_ms,
                        })

                    elif isinstance(event, StepLog):
                        await bus.publish(run_id, "step.log", {
                            "index": event.index, "message": event.message,
                        })

                    elif isinstance(event, RunError):
                        raise RuntimeError(event.message)

                elapsed = int((time.monotonic() - t0) * 1000)
                final_status = "failed" if summary.get("failed", 0) > 0 else "passed"
                run_q.update_run_status(
                    db, run_id, final_status,
                    finished_at=datetime.now(timezone.utc),
                    duration_ms=elapsed,
                    step_summary=summary,
                )
                await bus.publish(run_id, "run.completed", {
                    "run_id": run_id, "status": final_status,
                    "step_summary": summary, "duration_ms": elapsed,
                })

            except Exception as e:
                run_q.update_run_status(db, run_id, "error", finished_at=datetime.now(timezone.utc))
                await bus.publish(run_id, "run.error", {"run_id": run_id, "status": "error", "message": str(e)})

            finally:
                await bus.close(run_id)
