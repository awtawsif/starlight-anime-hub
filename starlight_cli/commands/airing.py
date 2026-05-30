import json
import sys

import click
from rich.table import Table

from starlight_cli.cli import cli, console, err_console
from starlight_cli._helpers import _assign_code
from starlight_cli.api import fetch_airing_anime


@cli.command()
@click.option("--page", default=1, type=int, help="Page number")
def airing(page):
    ctx = click.get_current_context()
    anime, pagination, error = fetch_airing_anime(page)

    if ctx.parent.obj.get("json"):
        sys.stdout.write(json.dumps({"data": anime, "pagination": pagination, "error": error}) + "\n")
        return

    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not anime:
        console.print("[yellow]No currently airing anime found.[/]")
        sys.exit(1)

    cur = pagination.get("current_page", 1)
    last = pagination.get("last_page", 1)

    table = Table(title=f"Latest Releases (page {cur}/{last})")
    table.add_column("Code", style="cyan", width=6)
    table.add_column("Title", style="white")
    table.add_column("Episode")
    table.add_column("Fansub")
    table.add_column("Aired")

    for a in anime:
        code = (
            _assign_code(
                a.get("anime_title", ""), a.get("anime_session", "")
            )
            or ""
        )
        table.add_row(
            code,
            a.get("anime_title", "N/A"),
            str(a.get("episode", "")),
            a.get("fansub", ""),
            a.get("created_at", "").split(" ")[0],
        )

    console.print(table)
