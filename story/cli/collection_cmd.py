from __future__ import annotations

import click

from story.cli.client import get_client
from story.cli.formatters import print_table, print_kv, console


@click.group("collection")
def collection_group():
    """Manage story collections."""
    pass


@collection_group.command("create")
@click.argument("name")
@click.option("--description", default=None)
@click.option("--target", default=None)
@click.option("--harness", default=None)
@click.pass_context
def collection_create(ctx, name, description, target, harness):
    """Create a story collection."""
    client = get_client(ctx)
    data = {"name": name}
    if description:
        data["description"] = description
    if target:
        data["target"] = target
    if harness:
        data["harness"] = harness
    result = client.post("/api/v1/collections", data)
    click.echo(f"Collection '{result['name']}' created ({result['id']})")


@collection_group.command("list")
@click.pass_context
def collection_list(ctx):
    """List all collections."""
    client = get_client(ctx)
    result = client.get("/api/v1/collections")
    rows = []
    for c in result["items"]:
        rows.append([c["name"], str(c.get("story_count", 0)), c.get("target") or "-", c.get("created_at", "")[:16]])
    print_table(["NAME", "STORIES", "TARGET", "CREATED"], rows)


@collection_group.command("show")
@click.argument("name_or_id")
@click.pass_context
def collection_show(ctx, name_or_id):
    """Show collection details."""
    client = get_client(ctx)
    c = client.get(f"/api/v1/collections/{name_or_id}")
    print_kv([
        ("Name:", c["name"]),
        ("ID:", c["id"]),
        ("Description:", c.get("description")),
        ("Target:", c.get("target")),
        ("Harness:", c.get("harness")),
        ("Stories:", str(c.get("story_count", 0))),
        ("Created:", c.get("created_at")),
    ])
    stories = c.get("stories", [])
    if stories:
        console.print("\n[bold]STORIES:[/bold]")
        rows = [[str(i + 1), s["title"], s["scene"]] for i, s in enumerate(stories)]
        print_table(["#", "TITLE", "SCENE"], rows)


@collection_group.command("update")
@click.argument("name_or_id")
@click.option("--name", "new_name", default=None)
@click.option("--description", default=None)
@click.option("--target", default=None)
@click.option("--harness", default=None)
@click.pass_context
def collection_update(ctx, name_or_id, new_name, description, target, harness):
    """Update collection info."""
    client = get_client(ctx)
    data = {}
    if new_name:
        data["name"] = new_name
    if description:
        data["description"] = description
    if target:
        data["target"] = target
    if harness:
        data["harness"] = harness
    if not data:
        click.echo("Nothing to update.")
        return
    result = client.patch(f"/api/v1/collections/{name_or_id}", data)
    click.echo(f"Collection '{result['name']}' updated.")


@collection_group.command("remove")
@click.argument("name_or_id")
@click.option("--cascade", is_flag=True, help="Also delete stories and runs")
@click.pass_context
def collection_remove(ctx, name_or_id, cascade):
    """Delete a collection."""
    client = get_client(ctx)
    params = {"cascade": "true"} if cascade else {}
    client.delete(f"/api/v1/collections/{name_or_id}", params=params)
    click.echo(f"Collection '{name_or_id}' removed.")


@collection_group.command("run")
@click.argument("name_or_id")
@click.option("--target", default=None)
@click.option("--harness", default=None)
@click.option("--no-stream", is_flag=True)
@click.pass_context
def collection_run(ctx, name_or_id, target, harness, no_stream):
    """Execute all stories in a collection."""
    client = get_client(ctx)
    data = {}
    if target:
        data["target"] = target
    if harness:
        data["harness"] = harness
    result = client.post(f"/api/v1/collections/{name_or_id}/runs", data or None)

    batch_id = result.get("batch_id", "?")
    runs = result.get("runs", [])
    click.echo(f"Batch {batch_id} started — {len(runs)} stories\n")

    if no_stream:
        for r in runs:
            click.echo(f"  {r.get('story_title', r['story_id'])} → {r['id']}")
        return

    for i, r in enumerate(runs, 1):
        click.echo(f"[{i}/{len(runs)}] {r.get('story_title', r['story_id'])}")
        _stream_run(client, r["id"])
        click.echo()

    click.echo(f"Batch complete: {len(runs)} stories submitted")


def _stream_run(client, run_id: str) -> None:
    current_chapter = ""
    for event_type, data in client.stream_sse(f"/api/v1/runs/{run_id}/stream"):
        if event_type == "step.started":
            chapter = data.get("chapter", "")
            if chapter != current_chapter:
                current_chapter = chapter
                console.print(f"\n  [bold]{chapter}[/bold]")
            desc = data.get("description", "")
            console.print(f"    ⏳ {desc}", end="")
        elif event_type == "step.completed":
            status = data.get("status", "?")
            ms = data.get("duration_ms", 0)
            mark = "✓" if status == "passed" else "✗"
            color = "green" if status == "passed" else "red"
            console.print(f"\r    [{color}]{mark}[/{color}] ... ({ms}ms)")
        elif event_type == "run.completed":
            summary = data.get("step_summary", {})
            status = data.get("status", "?")
            ms = data.get("duration_ms", 0)
            color = "green" if status == "passed" else "red"
            console.print(f"\n  [{color}]{status.upper()}[/{color}]  {summary.get('passed', 0)}/{summary.get('total', 0)} steps  {ms / 1000:.1f}s")
        elif event_type == "run.error":
            console.print(f"\n  [red]ERROR: {data.get('message', '?')}[/red]")
