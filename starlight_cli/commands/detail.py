import json
import sys

import click
from rich.panel import Panel
from rich.table import Table

from starlight_cli.cli import cli, console, err_console
from starlight_cli._helpers import _resolve_anime
from starlight_cli import state
from starlight_cli.api import fetch_anime_details


@cli.command()
@click.argument("anime")
def detail(anime):
    ctx = click.get_current_context()
    session_id, title = _resolve_anime(anime)
    details, error = fetch_anime_details(session_id)

    if ctx.parent.obj.get("json"):
        sys.stdout.write(json.dumps({"details": details, "error": error}) + "\n")
        return

    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    code = state.get_session_code(session_id)
    panel_title = f"{title}" + (f"  [dim]({code})[/]" if code else "")

    info = (
        f"[bold]Title:[/]       {details.get('title', 'N/A')}\n"
        f"[bold]Type:[/]        {details.get('type', 'N/A')}\n"
        f"[bold]Episodes:[/]    {details.get('episodes', 'N/A')}\n"
        f"[bold]Status:[/]      {details.get('status', 'N/A')}\n"
        f"[bold]Aired:[/]       {details.get('aired', 'N/A')}\n"
        f"[bold]Duration:[/]    {details.get('duration', 'N/A')}\n"
        f"[bold]Season:[/]      {details.get('season', 'N/A')}\n"
        f"[bold]Studio:[/]      {details.get('studio', 'N/A')}\n"
        f"[bold]Genre:[/]       {details.get('genre', 'N/A')}\n"
        f"[bold]Theme:[/]       {details.get('theme', 'N/A')}\n"
        f"[bold]Demographic:[/] {details.get('demographic', 'N/A')}\n"
        f"[bold]Synonyms:[/]    {details.get('synonyms', 'N/A')}\n"
        f"[bold]Japanese:[/]    {details.get('japanese', 'N/A')}"
    )

    console.print(Panel(info, title=panel_title, border_style="cyan"))
    console.print(
        Panel(
            details.get("synopsis", "No synopsis available."),
            title="Synopsis",
            border_style="green",
        )
    )

    for section, key in [
        ("Relations", "relations"),
        ("Recommendations", "recommendations"),
    ]:
        items = details.get(key, [])
        if items:
            t = Table(title=section)
            t.add_column("Title", style="white")
            t.add_column("Type")
            for item in items[:4]:
                t.add_row(item.get("title", "N/A"), item.get("type", "N/A"))
            if len(items) > 4:
                t.add_row(f"[dim]... and {len(items) - 4} more[/]", "")
            console.print(t)
