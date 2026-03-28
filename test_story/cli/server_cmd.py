from __future__ import annotations

import os
import signal
import subprocess
import sys
from pathlib import Path

import click

from test_story.cli.client import get_client
from test_story.cli.formatters import print_kv

PID_FILE = Path.home() / ".test-story" / "server.pid"


@click.group("server")
def server_group():
    """Server management."""
    pass


@server_group.command("start")
@click.option("--port", "-p", default=3000, help="Port")
@click.option("--harness", default=None, help="Default harness")
@click.option("--provider", default=None, help="Default provider")
@click.option("--daemon", "-d", is_flag=True, help="Run in background")
@click.pass_context
def server_start(ctx, port, harness, provider, daemon):
    """Start the server."""
    if daemon:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "test_story.server.app:create_app",
             "--factory", "--host", "0.0.0.0", "--port", str(port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        PID_FILE.write_text(str(proc.pid))
        click.echo(f"Server started on port {port} (PID: {proc.pid})")
    else:
        click.echo(f"Starting server on port {port}...")
        import uvicorn
        from test_story.server.app import create_app
        uvicorn.run(create_app(), host="0.0.0.0", port=port)


@server_group.command("stop")
def server_stop():
    """Stop the background server."""
    if not PID_FILE.exists():
        click.echo("No server PID file found.")
        return
    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        click.echo(f"Server (PID: {pid}) stopped.")
    except ProcessLookupError:
        click.echo(f"Process {pid} not found.")
    PID_FILE.unlink(missing_ok=True)


@server_group.command("status")
@click.pass_context
def server_status(ctx):
    """Show server status."""
    client = get_client(ctx)
    try:
        health = client.get("/healthz")
        config = client.get("/api/v1/config")
        uptime_s = health.get("uptime_seconds", 0)
        h = uptime_s // 3600
        m = (uptime_s % 3600) // 60
        s = uptime_s % 60
        print_kv([
            ("Server:", ctx.obj["server"]),
            ("Status:", "running"),
            ("Version:", health.get("version", "?")),
            ("Uptime:", f"{h}h {m}m {s}s"),
            ("Harness:", config.get("harness", "-")),
            ("Provider:", config.get("provider", "-")),
            ("Scenes:", ", ".join(config.get("supported_scenes", []))),
        ])
    except Exception:
        click.echo("Server is not running or unreachable.")


@server_group.command("config")
@click.option("--harness", default=None)
@click.option("--provider", default=None)
@click.option("--max-concurrent-runs", type=int, default=None)
@click.pass_context
def server_config(ctx, harness, provider, max_concurrent_runs):
    """View or update server config."""
    client = get_client(ctx)
    if harness or provider or max_concurrent_runs:
        data = {}
        if harness:
            data["harness"] = harness
        if provider:
            data["provider"] = provider
        if max_concurrent_runs:
            data["max_concurrent_runs"] = max_concurrent_runs
        config = client.patch("/api/v1/config", data)
    else:
        config = client.get("/api/v1/config")
    print_kv([
        ("Harness:", config.get("harness")),
        ("Provider:", config.get("provider")),
        ("Scenes:", ", ".join(config.get("supported_scenes", []))),
        ("Max Concurrent:", str(config.get("max_concurrent_runs"))),
    ])
