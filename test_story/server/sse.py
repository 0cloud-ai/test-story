from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass


@dataclass
class SSEMessage:
    event: str
    data: dict


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, run_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(run_id, []).append(q)
        return q

    def unsubscribe(self, run_id: str, q: asyncio.Queue) -> None:
        subs = self._subscribers.get(run_id, [])
        if q in subs:
            subs.remove(q)
        if not subs:
            self._subscribers.pop(run_id, None)

    async def publish(self, run_id: str, event: str, data: dict) -> None:
        msg = SSEMessage(event=event, data=data)
        for q in self._subscribers.get(run_id, []):
            await q.put(msg)

    async def close(self, run_id: str) -> None:
        for q in self._subscribers.get(run_id, []):
            await q.put(None)
        self._subscribers.pop(run_id, None)


def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"
