from __future__ import annotations

import click

from test_story.cli.server_cmd import server_group
from test_story.cli.provider_cmd import provider_group
from test_story.cli.harness_cmd import harness_group
from test_story.cli.collection_cmd import collection_group
from test_story.cli.story_cmd import story_group
from test_story.cli.run_cmd import run_group


@click.group()
@click.option("--server", "-s", default="http://localhost:3000", help="Server address")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@click.pass_context
def main(ctx, server, output):
    """test-story: A story-driven test framework."""
    ctx.ensure_object(dict)
    ctx.obj["server"] = server
    ctx.obj["output"] = output


main.add_command(server_group, "server")
main.add_command(provider_group, "provider")
main.add_command(harness_group, "harness")
main.add_command(collection_group, "collection")
main.add_command(story_group, "story")
main.add_command(run_group, "run")
