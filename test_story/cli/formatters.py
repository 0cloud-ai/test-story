from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console()


def print_table(columns: list[str], rows: list[list[str]]) -> None:
    table = Table()
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[str(c) if c is not None else "-" for c in row])
    console.print(table)


def print_kv(pairs: list[tuple[str, str]]) -> None:
    max_key = max(len(k) for k, _ in pairs) if pairs else 0
    for key, val in pairs:
        console.print(f"[bold]{key:<{max_key}}[/bold]  {val if val is not None else '-'}")
