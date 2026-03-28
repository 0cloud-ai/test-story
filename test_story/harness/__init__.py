from __future__ import annotations

from test_story.harness.base import AbstractHarness
from test_story.harness.claude_code import ClaudeCodeHarness
from test_story.harness.claude_agent_sdk import ClaudeAgentSDKHarness
from test_story.harness.opencode import OpenCodeHarness

_registry: dict[str, AbstractHarness] = {
    "claude-code": ClaudeCodeHarness(),
    "claude-agent-sdk": ClaudeAgentSDKHarness(),
    "opencode": OpenCodeHarness(),
}


def get_harness_impl(name: str) -> AbstractHarness:
    impl = _registry.get(name)
    if not impl:
        raise ValueError(f"Unknown harness: {name}")
    return impl
