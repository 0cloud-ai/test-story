from __future__ import annotations

import json
import sys

import click
import httpx


class Client:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30)

    def get(self, path: str, params: dict | None = None) -> dict:
        resp = self._client.get(path, params=params)
        return self._handle(resp)

    def post(self, path: str, json_data: dict | None = None) -> dict:
        resp = self._client.post(path, json=json_data)
        return self._handle(resp)

    def post_file(self, path: str, filepath: str, options: dict | None = None) -> dict:
        with open(filepath, "rb") as f:
            files = {"story": (filepath, f, "text/markdown")}
            data = {"options": json.dumps(options)} if options else {}
            resp = self._client.post(path, files=files, data=data)
        return self._handle(resp)

    def post_markdown(self, path: str, content: str) -> dict:
        resp = self._client.post(path, content=content, headers={"Content-Type": "text/markdown"})
        return self._handle(resp)

    def put_markdown(self, path: str, content: str) -> dict:
        resp = self._client.put(path, content=content, headers={"Content-Type": "text/markdown"})
        return self._handle(resp)

    def patch(self, path: str, json_data: dict) -> dict:
        resp = self._client.patch(path, json=json_data)
        return self._handle(resp)

    def delete(self, path: str, params: dict | None = None) -> None:
        resp = self._client.delete(path, params=params)
        if resp.status_code == 204:
            return
        self._handle(resp)

    def stream_sse(self, path: str):
        with self._client.stream("GET", path, headers={"Accept": "text/event-stream"}) as resp:
            if resp.status_code != 200:
                body = b""
                for chunk in resp.iter_bytes():
                    body += chunk
                err = json.loads(body)
                click.echo(f"Error: {err.get('error', {}).get('message', 'Unknown')}", err=True)
                return

            event_type = ""
            data_buf = ""
            for line in resp.iter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data_buf = line[6:]
                elif line == "":
                    if event_type and data_buf:
                        yield event_type, json.loads(data_buf)
                    event_type = ""
                    data_buf = ""

    def _handle(self, resp: httpx.Response) -> dict:
        if resp.status_code >= 400:
            try:
                body = resp.json()
                msg = body.get("error", {}).get("message", resp.text)
            except Exception:
                msg = resp.text
            click.echo(f"Error ({resp.status_code}): {msg}", err=True)
            sys.exit(1)
        if resp.status_code == 204:
            return {}
        return resp.json()


def get_client(ctx: click.Context) -> Client:
    return Client(ctx.obj["server"])
