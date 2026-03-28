from __future__ import annotations

import click

from test_story.cli.client import get_client
from test_story.cli.formatters import print_table, print_kv, console


@click.group("run")
def run_group():
    """Execute a story or manage runs."""
    pass


@run_group.command("start")
@click.argument("file")
@click.option("--target", default=None)
@click.option("--harness", default=None)
@click.option("--collection", default=None)
@click.option("--env", multiple=True, help="KEY=VALUE")
@click.option("--no-stream", is_flag=True)
@click.pass_context
def run_start(ctx, file, target, harness, collection, env, no_stream):
    """Execute a story file (quick run)."""
    client = get_client(ctx)
    options = {}
    if target:
        options["target"] = target
    if harness:
        options["harness"] = harness
    if collection:
        options["collection_id"] = collection
    if env:
        env_dict = {}
        for e in env:
            k, _, v = e.partition("=")
            env_dict[k] = v
        options["env"] = env_dict

    result = client.post_file("/api/v1/runs", file, options=options or None)
    story_info = result.get("story", {})
    run_info = result.get("run", {})
    run_id = run_info.get("id", "?")

    console.print(f"Story: {story_info.get('title', '?')} ({story_info.get('id', '?')})")
    console.print(f"Run:   {run_id}")
    console.print()

    if no_stream:
        click.echo(f"Run {run_id} queued.")
        return

    _stream_run(client, run_id)


@run_group.command("exec")
@click.argument("story_id")
@click.option("--target", default=None)
@click.option("--harness", default=None)
@click.option("--env", multiple=True, help="KEY=VALUE")
@click.option("--no-stream", is_flag=True)
@click.pass_context
def run_exec(ctx, story_id, target, harness, env, no_stream):
    """Execute an existing story."""
    client = get_client(ctx)
    data = {}
    if target:
        data["target"] = target
    if harness:
        data["harness"] = harness
    if env:
        env_dict = {}
        for e in env:
            k, _, v = e.partition("=")
            env_dict[k] = v
        data["env"] = env_dict

    result = client.post(f"/api/v1/stories/{story_id}/runs", data or None)
    run_id = result.get("id", "?")
    console.print(f"Run: {run_id}")
    console.print()

    if no_stream:
        click.echo(f"Run {run_id} queued.")
        return

    _stream_run(client, run_id)


@run_group.command("list")
@click.option("--story", "story_id", default=None)
@click.option("--collection", "collection_id", default=None)
@click.option("--batch", "batch_id", default=None)
@click.option("--status", default=None)
@click.pass_context
def run_list(ctx, story_id, collection_id, batch_id, status):
    """List runs."""
    client = get_client(ctx)
    params = {}
    if story_id:
        params["story_id"] = story_id
    if collection_id:
        params["collection_id"] = collection_id
    if batch_id:
        params["batch_id"] = batch_id
    if status:
        params["status"] = status
    result = client.get("/api/v1/runs", params=params)
    rows = []
    for r in result["items"]:
        summary = r.get("step_summary") or {}
        steps = f"{summary.get('passed', 0)}/{summary.get('total', 0)}" if summary else "-"
        dur = f"{r['duration_ms'] / 1000:.1f}s" if r.get("duration_ms") else "-"
        rows.append([r["id"], r.get("story_title") or r["story_id"], r["status"], steps, dur])
    print_table(["RUN ID", "STORY", "STATUS", "STEPS", "DURATION"], rows)


@run_group.command("show")
@click.argument("run_id")
@click.option("--steps", is_flag=True, help="Show all step details")
@click.option("--failed", is_flag=True, help="Show only failed steps")
@click.pass_context
def run_show(ctx, run_id, steps, failed):
    """Show run details."""
    client = get_client(ctx)
    r = client.get(f"/api/v1/runs/{run_id}")
    summary = r.get("step_summary") or {}
    print_kv([
        ("Run:", r["id"]),
        ("Story:", f"{r.get('story_title', '?')} ({r['story_id']})"),
        ("Status:", r["status"]),
        ("Harness:", r.get("harness")),
        ("Target:", r.get("target")),
        ("Steps:", f"{summary.get('passed', 0)}/{summary.get('total', 0)} passed"),
        ("Duration:", f"{r['duration_ms'] / 1000:.1f}s" if r.get("duration_ms") else "-"),
        ("Created:", r.get("created_at")),
        ("Finished:", r.get("finished_at")),
    ])

    run_steps = r.get("steps", [])
    if not run_steps:
        return

    if failed:
        run_steps = [s for s in run_steps if s.get("status") == "failed"]

    if steps or failed:
        console.print("\n[bold]STEPS:[/bold]")
        for s in run_steps:
            st = s.get("status", "?")
            mark = "✓" if st == "passed" else "✗" if st == "failed" else "?"
            color = "green" if st == "passed" else "red" if st == "failed" else "yellow"
            ms = s.get("duration_ms", 0)
            console.print(f"  [{color}]{mark}[/{color}] #{s['index']} {s.get('chapter', '')} — {s.get('description', '')} ({ms}ms)")

            if st == "failed" and s.get("assertions"):
                for a in s["assertions"]:
                    if not a.get("passed"):
                        console.print(f"      Expected: {a.get('expected', '?')}")
                        console.print(f"      Actual:   {a.get('actual', '?')}")
    else:
        console.print("\n[bold]STEPS:[/bold]")
        step_rows = []
        for s in run_steps:
            step_rows.append([
                str(s["index"]),
                s.get("chapter") or "",
                s.get("description") or "",
                s.get("status", "?"),
                f"{s.get('duration_ms', 0)}ms",
            ])
        print_table(["#", "CHAPTER", "DESCRIPTION", "STATUS", "DURATION"], step_rows)


@run_group.command("cancel")
@click.argument("run_id")
@click.pass_context
def run_cancel(ctx, run_id):
    """Cancel a run."""
    client = get_client(ctx)
    client.post(f"/api/v1/runs/{run_id}/cancel")
    click.echo(f"Run {run_id} cancelled.")


@run_group.command("retry")
@click.argument("run_id")
@click.option("--no-stream", is_flag=True)
@click.pass_context
def run_retry(ctx, run_id, no_stream):
    """Retry a run with same parameters."""
    client = get_client(ctx)
    result = client.post(f"/api/v1/runs/{run_id}/retry")
    new_id = result.get("id", "?")
    console.print(f"New run {new_id} created.")

    if no_stream:
        return

    _stream_run(client, new_id)


def _stream_run(client, run_id: str) -> None:
    current_chapter = ""
    for event_type, data in client.stream_sse(f"/api/v1/runs/{run_id}/stream"):
        if event_type == "step.started":
            chapter = data.get("chapter", "")
            if chapter != current_chapter:
                current_chapter = chapter
                console.print(f"\n[bold]{chapter}[/bold]")
            desc = data.get("description", "")
            console.print(f"  ⏳ {desc}", end="\r")
        elif event_type == "step.completed":
            status = data.get("status", "?")
            ms = data.get("duration_ms", 0)
            desc = data.get("description", "")
            mark = "✓" if status == "passed" else "✗"
            color = "green" if status == "passed" else "red"
            console.print(f"  [{color}]{mark}[/{color}] {desc} ({ms}ms)          ")
        elif event_type == "run.completed":
            summary = data.get("step_summary", {})
            status = data.get("status", "?")
            ms = data.get("duration_ms", 0)
            color = "green" if status == "passed" else "red"
            console.print(f"\n[{color}]{status.upper()}[/{color}]  {summary.get('passed', 0)}/{summary.get('total', 0)} steps  {ms / 1000:.1f}s")
        elif event_type == "run.error":
            console.print(f"\n[red]ERROR: {data.get('message', '?')}[/red]")
