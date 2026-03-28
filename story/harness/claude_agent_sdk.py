from __future__ import annotations

from typing import AsyncIterator

from story.harness.claude_code import ClaudeCodeHarness
from story.harness.base import AbstractHarness, StepEvent


class ClaudeAgentSDKHarness(ClaudeCodeHarness):
    name = "claude-agent-sdk"
