import json
import sys

import click
from rich.table import Table

from starlight_cli.cli import cli, console, err_console
from starlight_cli._helpers import _resolve_anime
from starlight_cli.api import fetch_episode_list


@cli.command()
@click.argument("anime")
@click.option("--page", default=1, type=int)
@click.option(
    "--sort",
    default="episode_asc",
    type=click.Choice(["episode_asc", "episode_desc"]),
)
def episodes(anime, page, sort):
    ctx = click.get_current_context()
    session_id, title = _resolve_anime(anime)

    batch, pagination, error = fetch_episode_list(session_id, page, sort)

    if ctx.parent.obj.get("json"):
        sys.stdout.write(json.dumps({"episodes": batch, "pagination": pagination, "error": error}) + "\n")
        return

    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not batch:
        console.print("[yellow]No episodes found.[/]")
        sys.exit(1)

    cur = pagination.get("current_page", 1)
    last = pagination.get("last_page", 1)

    table = Table(title=f"{title}  —  Episodes (page {cur}/{last})")
    table.add_column("#", style="cyan")
    table.add_column("Duration")
    table.add_column("Filler")

    for ep in batch:
        table.add_row(
            str(ep.get("episode", "")),
            str(ep.get("duration", "")),
            "[red]Yes[/]" if ep.get("filler") else "",
        )

    console.print(table)
