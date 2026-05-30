import json
import sys

import click
from rich.table import Table

from starlight_cli.cli import cli, console, err_console
from starlight_cli._helpers import _assign_code
from starlight_cli.api import fetch_anime_search_results


@cli.command()
@click.argument("query")
def search(query):
    ctx = click.get_current_context()
    results, error = fetch_anime_search_results(query)

    if ctx.parent.obj.get("json"):
        sys.stdout.write(json.dumps({"results": results, "error": error}) + "\n")
        return

    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not results:
        console.print("[yellow]No results found.[/]")
        sys.exit(1)

    table = Table(title=f"Search results for '{query}'")
    table.add_column("Code", style="cyan", width=6)
    table.add_column("Title", style="white")
    table.add_column("Type")
    table.add_column("Episodes")
    table.add_column("Score")
    table.add_column("Status")

    for r in results:
        code = _assign_code(r.get("title", ""), r.get("session", "")) or "?"
        table.add_row(
            code,
            r.get("title", "N/A"),
            r.get("type", "N/A"),
            str(r.get("episodes", "N/A")),
            f'{r.get("score", ""):.2f}' if r.get("score") else "N/A",
            r.get("status", "N/A"),
        )

    console.print(table)
    console.print(
        "\nUse [bold]starlight detail <code>[/] for more information, "
        "or [bold]starlight watch <code>[/] to start watching."
    )
