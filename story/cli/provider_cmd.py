from __future__ import annotations

import click

from story.cli.client import get_client
from story.cli.formatters import print_table, print_kv


@click.group("provider")
def provider_group():
    """Manage LLM providers."""
    pass


@provider_group.command("add")
@click.argument("name")
@click.option("--type", "ptype", required=True, help="Provider type")
@click.option("--base-url", required=True, help="API base URL")
@click.option("--api-key", default=None, help="API key")
@click.option("--model", required=True, help="Model identifier")
@click.option("--max-tokens", type=int, default=16384, help="Max tokens")
@click.pass_context
def provider_add(ctx, name, ptype, base_url, api_key, model, max_tokens):
    """Register a new provider."""
    client = get_client(ctx)
    data = {
        "name": name,
        "type": ptype,
        "config": {"base_url": base_url, "model": model, "max_tokens": max_tokens},
    }
    if api_key:
        data["config"]["api_key"] = api_key
    result = client.post("/api/v1/providers", data)
    click.echo(f"Provider '{result['name']}' created ({result['id']})")


@provider_group.command("list")
@click.option("--type", "ptype", default=None)
@click.pass_context
def provider_list(ctx, ptype):
    """List all providers."""
    client = get_client(ctx)
    params = {}
    if ptype:
        params["type"] = ptype
    result = client.get("/api/v1/providers", params=params)
    rows = []
    for item in result["items"]:
        cfg = item.get("config", {})
        rows.append([item["name"], item["type"], cfg.get("model", "-"), cfg.get("base_url", "-")])
    print_table(["NAME", "TYPE", "MODEL", "BASE URL"], rows)


@provider_group.command("show")
@click.argument("name_or_id")
@click.pass_context
def provider_show(ctx, name_or_id):
    """Show provider details."""
    client = get_client(ctx)
    p = client.get(f"/api/v1/providers/{name_or_id}")
    cfg = p.get("config", {})
    print_kv([
        ("Name:", p["name"]),
        ("ID:", p["id"]),
        ("Type:", p["type"]),
        ("Base URL:", cfg.get("base_url")),
        ("API Key:", cfg.get("api_key")),
        ("Model:", cfg.get("model")),
        ("Max Tokens:", str(cfg.get("max_tokens"))),
        ("Created:", p.get("created_at")),
    ])


@provider_group.command("update")
@click.argument("name_or_id")
@click.option("--model", default=None)
@click.option("--base-url", default=None)
@click.option("--api-key", default=None)
@click.option("--max-tokens", type=int, default=None)
@click.pass_context
def provider_update(ctx, name_or_id, model, base_url, api_key, max_tokens):
    """Update provider configuration."""
    client = get_client(ctx)
    cfg = {}
    if model:
        cfg["model"] = model
    if base_url:
        cfg["base_url"] = base_url
    if api_key:
        cfg["api_key"] = api_key
    if max_tokens:
        cfg["max_tokens"] = max_tokens
    if not cfg:
        click.echo("Nothing to update.")
        return
    result = client.patch(f"/api/v1/providers/{name_or_id}", {"config": cfg})
    click.echo(f"Provider '{result['name']}' updated.")


@provider_group.command("remove")
@click.argument("name_or_id")
@click.pass_context
def provider_remove(ctx, name_or_id):
    """Delete a provider."""
    client = get_client(ctx)
    client.delete(f"/api/v1/providers/{name_or_id}")
    click.echo(f"Provider '{name_or_id}' removed.")
