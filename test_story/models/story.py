from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


@dataclass
class StoryMeta:
    title: str
    target: str | None = None
    scene: str = "api"


def parse_meta(markdown: str) -> StoryMeta:
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    meta_match = re.search(r"```meta\s*\n(.*?)```", markdown, re.DOTALL)
    target = None
    scene = "api"
    if meta_match:
        for line in meta_match.group(1).strip().splitlines():
            line = line.strip()
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                if key == "target":
                    target = val
                elif key == "scene":
                    scene = val

    return StoryMeta(title=title, target=target, scene=scene)


class Story(BaseModel):
    id: str
    collection_id: str | None = None
    title: str
    scene: str
    target: str | None = None
    content: str | None = None
    created_at: datetime
    updated_at: datetime
