from __future__ import annotations

import click

from story.cli.client import get_client
from story.cli.formatters import print_table, print_kv


@click.group("harness")
def harness_group():
    """Manage harness engines."""
    pass


@harness_group.command("list")
@click.pass_context
def harness_list(ctx):
    """List all harnesses."""
    client = get_client(ctx)
    items = client.get("/api/v1/harnesses")
    rows = []
    for h in items:
        rows.append([
            h["name"],
            "yes" if h["available"] else "no",
            h.get("version") or "-",
            h.get("provider") or "-",
        ])
    print_table(["NAME", "AVAILABLE", "VERSION", "PROVIDER"], rows)


@harness_group.command("show")
@click.argument("name")
@click.pass_context
def harness_show(ctx, name):
    """Show harness details."""
    client = get_client(ctx)
    h = client.get(f"/api/v1/harnesses/{name}")
    cfg = h.get("config", {})
    print_kv([
        ("Name:", h["name"]),
        ("Available:", "yes" if h["available"] else "no"),
        ("Version:", h.get("version")),
        ("Provider:", h.get("provider")),
        ("Timeout:", f"{cfg.get('timeout_seconds', 300)}s"),
    ])
    if h.get("reason"):
        print_kv([("Reason:", h["reason"])])


@harness_group.command("set")
@click.argument("name")
@click.option("--provider", default=None, help="Associate LLM provider")
@click.option("--timeout", type=int, default=None, help="Timeout in seconds")
@click.pass_context
def harness_set(ctx, name, provider, timeout):
    """Update harness configuration."""
    client = get_client(ctx)
    data = {}
    if provider:
        data["provider"] = provider
    if timeout:
        data["config"] = {"timeout_seconds": timeout}
    if not data:
        click.echo("Nothing to update.")
        return
    result = client.patch(f"/api/v1/harnesses/{name}", data)
    click.echo(f"Harness '{result['name']}' updated.")
