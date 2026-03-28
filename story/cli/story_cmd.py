from __future__ import annotations

import glob as globmod
from pathlib import Path

import click

from story.cli.client import get_client
from story.cli.formatters import print_table, print_kv, console


@click.group("story")
def story_group():
    """Manage stories."""
    pass


@story_group.command("add")
@click.argument("collection")
@click.argument("files", nargs=-1, required=True)
@click.pass_context
def story_add(ctx, collection, files):
    """Add stories to a collection."""
    client = get_client(ctx)
    # Resolve the collection name/id
    coll = client.get(f"/api/v1/collections/{collection}")
    coll_id = coll["id"]

    expanded = []
    for f in files:
        matches = globmod.glob(f)
        expanded.extend(matches if matches else [f])

    for filepath in expanded:
        content = Path(filepath).read_text(encoding="utf-8")
        result = client.post_markdown(f"/api/v1/collections/{coll_id}/stories", content)
        click.echo(f"Added '{filepath}' → {result['title']} ({result['id']})")


@story_group.command("list")
@click.argument("collection")
@click.option("--scene", default=None)
@click.pass_context
def story_list(ctx, collection, scene):
    """List stories in a collection."""
    client = get_client(ctx)
    coll = client.get(f"/api/v1/collections/{collection}")
    params = {}
    if scene:
        params["scene"] = scene
    result = client.get(f"/api/v1/collections/{coll['id']}/stories", params=params)
    rows = []
    for s in result["items"]:
        rows.append([s["id"], s["title"], s["scene"], s.get("target") or "-"])
    print_table(["ID", "TITLE", "SCENE", "TARGET"], rows)


@story_group.command("show")
@click.argument("story_id")
@click.option("--content", is_flag=True, help="Show full markdown content")
@click.pass_context
def story_show(ctx, story_id, content):
    """Show story details."""
    client = get_client(ctx)
    s = client.get(f"/api/v1/stories/{story_id}")
    print_kv([
        ("Title:", s["title"]),
        ("ID:", s["id"]),
        ("Collection:", s.get("collection_id") or "-"),
        ("Scene:", s["scene"]),
        ("Target:", s.get("target")),
        ("Created:", s.get("created_at")),
        ("Updated:", s.get("updated_at")),
    ])
    if content and s.get("content"):
        console.print("\n[bold]Content:[/bold]")
        console.print(s["content"])


@story_group.command("update")
@click.argument("story_id")
@click.argument("file")
@click.pass_context
def story_update(ctx, story_id, file):
    """Replace story content."""
    client = get_client(ctx)
    content = Path(file).read_text(encoding="utf-8")
    result = client.put_markdown(f"/api/v1/stories/{story_id}", content)
    click.echo(f"Story '{result['title']}' updated.")


@story_group.command("remove")
@click.argument("story_id")
@click.option("--cascade", is_flag=True)
@click.pass_context
def story_remove(ctx, story_id, cascade):
    """Delete a story."""
    client = get_client(ctx)
    params = {"cascade": "true"} if cascade else {}
    client.delete(f"/api/v1/stories/{story_id}", params=params)
    click.echo(f"Story '{story_id}' removed.")
