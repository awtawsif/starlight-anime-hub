import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from starlight.api_handlers import (
    fetch_airing_anime,
    fetch_anime_details,
    fetch_anime_search_results,
    fetch_episode_download_links,
    fetch_episode_list,
)

from starlight_cli import state
from starlight_cli.kwik import extract_video_url
from starlight_cli.player import play

console = Console()
err_console = Console(stderr=True)


def _fetch_all_episodes(session_id: str, sort: str = "episode_asc"):
    all_ep = []
    page = 1
    while True:
        batch, pagination, error = fetch_episode_list(session_id, page, sort)
        if error:
            err_console.print(f"[red]{error}[/]")
            return all_ep
        all_ep.extend(batch)
        if pagination.get("current_page", 1) >= pagination.get("last_page", 1):
            break
        page += 1
    return all_ep


def _pick_episode(session_id: str):
    with console.status("Fetching episodes..."):
        all_ep = _fetch_all_episodes(session_id)
    if not all_ep:
        err_console.print("[red]No episodes found for this anime.[/]")
        sys.exit(1)

    table = Table()
    table.add_column("#", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Duration")
    table.add_column("Filler")

    for ep in all_ep:
        filler = "[red]Yes[/]" if ep.get("filler") else ""
        table.add_row(
            str(ep.get("episode", "?")),
            ep.get("title", "") or "",
            str(ep.get("duration", "")),
            filler,
        )

    console.print(table)
    choice = Prompt.ask("Enter episode number")

    matched = [e for e in all_ep if str(e.get("episode")) == choice]
    if not matched:
        err_console.print(f"[red]Episode {choice} not found.[/]")
        sys.exit(1)

    return matched[0].get("session")


def _pick_quality(downloads: list[dict]) -> dict:
    if len(downloads) == 1:
        return downloads[0]

    console.print("\n[bold]Available qualities:[/]")
    for i, dl in enumerate(downloads, 1):
        console.print(f"  {i}. {dl['text']}")
    choice = Prompt.ask(
        "Select quality",
        choices=[str(i) for i in range(1, len(downloads) + 1)],
    )
    return downloads[int(choice) - 1]


def _resolve_and_play(session_id: str, episode_id: str | None, do_play: bool):
    if not episode_id:
        episode_id = _pick_episode(session_id)

    with console.status("Fetching download links..."):
        downloads, error = fetch_episode_download_links(session_id, episode_id)

    if error:
        err_console.print(f"[red]{error}[/]")
        sys.exit(1)
    if not downloads:
        err_console.print("[red]No download links found.[/]")
        sys.exit(1)

    selected = _pick_quality(downloads)
    kwik_url = selected["href"]

    with console.status("Extracting video URL from kwik.cx..."):
        try:
            video_url = extract_video_url(kwik_url)
        except Exception as e:
            err_console.print(f"[red]Failed to extract video URL:[/] {e}")
            sys.exit(1)

    if do_play:
        state.mark_watched(session_id, episode_id)
        console.print(f"[green]Streaming {selected['text']}...[/]")
        play(video_url)
    else:
        console.print(f"\n[bold green]Video URL:[/] {video_url}")


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

@click.group()
def cli():
    pass


@cli.command()
@click.argument("query")
def search(query):
    results, error = fetch_anime_search_results(query)
    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not results:
        console.print("[yellow]No results found.[/]")
        return

    table = Table(title=f"Search results for '{query}'")
    table.add_column("ID", style="cyan", width=38, no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Type")
    table.add_column("Episodes")
    table.add_column("Score")
    table.add_column("Status")

    for r in results:
        table.add_row(
            str(r.get("session", r.get("id", ""))),
            r.get("title", "N/A"),
            r.get("type", "N/A"),
            str(r.get("episodes", "N/A")),
            f'{r.get("score", ""):.2f}' if r.get("score") else "N/A",
            r.get("status", "N/A"),
        )

    console.print(table)
    console.print(
        "\nUse [bold]starlight detail <ID>[/] for more information."
    )


@cli.command()
@click.option("--page", default=1, type=int, help="Page number")
def airing(page):
    anime, pagination, error = fetch_airing_anime(page)
    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not anime:
        console.print("[yellow]No currently airing anime found.[/]")
        return

    cur = pagination.get("current_page", 1)
    last = pagination.get("last_page", 1)

    table = Table(
        title=f"Latest Releases (page {cur}/{last})",
    )
    table.add_column("Anime ID", style="cyan", width=38, no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Episode")
    table.add_column("Fansub")
    table.add_column("Aired")

    for a in anime:
        table.add_row(
            a.get("anime_session", "N/A"),
            a.get("anime_title", "N/A"),
            str(a.get("episode", "")),
            a.get("fansub", ""),
            a.get("created_at", "").split(" ")[0],
        )

    console.print(table)


@cli.command()
@click.argument("session_id")
def detail(session_id):
    details, error = fetch_anime_details(session_id)
    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

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

    console.print(
        Panel(info, title=details.get("title"), border_style="cyan")
    )
    console.print(
        Panel(
            details.get("synopsis", "No synopsis available."),
            title="Synopsis",
            border_style="green",
        )
    )

    for section, key in [("Relations", "relations"), ("Recommendations", "recommendations")]:
        items = details.get(key, [])
        if items:
            t = Table(title=section)
            t.add_column("Title", style="white")
            t.add_column("Type")
            t.add_column("ID", width=38, no_wrap=True)
            for item in items:
                t.add_row(
                    item.get("title", "N/A"),
                    item.get("type", "N/A"),
                    item.get("session_id", "N/A"),
                )
            console.print(t)


@cli.command()
@click.argument("session_id")
@click.option("--page", default=1, type=int)
@click.option(
    "--sort",
    default="episode_asc",
    type=click.Choice(["episode_asc", "episode_desc"]),
)
def episodes(session_id, page, sort):
    batch, pagination, error = fetch_episode_list(session_id, page, sort)
    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not batch:
        console.print("[yellow]No episodes found.[/]")
        return

    cur = pagination.get("current_page", 1)
    last = pagination.get("last_page", 1)

    table = Table(title=f"Episodes (page {cur}/{last})")
    table.add_column("#", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Duration")
    table.add_column("Filler")
    table.add_column("Session ID", width=38, no_wrap=True)

    for ep in batch:
        table.add_row(
            str(ep.get("episode", "")),
            ep.get("title", "N/A") or "",
            str(ep.get("duration", "")),
            "[red]Yes[/]" if ep.get("filler") else "",
            ep.get("session", "N/A"),
        )

    console.print(table)


@cli.command()
@click.argument("session_id")
@click.argument("episode_id", required=False)
def watch(session_id, episode_id):
    _resolve_and_play(session_id, episode_id, do_play=True)


@cli.command()
@click.argument("session_id")
@click.argument("episode_id", required=False)
def download(session_id, episode_id):
    _resolve_and_play(session_id, episode_id, do_play=False)


# ---------------------------------------------------------------------------
# Bookmarks subcommand group
# ---------------------------------------------------------------------------

@cli.group()
def bookmarks():
    pass


@bookmarks.command(name="list")
def bookmarks_list():
    bm = state.get_bookmarks()
    if not bm:
        console.print("[yellow]No bookmarks.[/]")
        return

    table = Table(title="Bookmarks")
    table.add_column("Session ID", style="cyan", width=38, no_wrap=True)
    table.add_column("Title", style="white")
    for aid, title in bm.items():
        table.add_row(aid, title)
    console.print(table)


@bookmarks.command()
@click.argument("anime_id")
def add(anime_id):
    if anime_id in state.get_bookmarks():
        console.print("[yellow]Already bookmarked.[/]")
        return
    details, error = fetch_anime_details(anime_id)
    title = details.get("title", anime_id) if not error else anime_id
    state.add_bookmark(anime_id, title)
    console.print(f"[green]Bookmarked:[/] {title}")


@bookmarks.command()
@click.argument("anime_id")
def remove(anime_id):
    if anime_id not in state.get_bookmarks():
        console.print("[yellow]Not bookmarked.[/]")
        return
    state.remove_bookmark(anime_id)
    console.print("[green]Removed bookmark.[/]")


# ---------------------------------------------------------------------------
# Continue-watching
# ---------------------------------------------------------------------------

@cli.command()
def continue_watching():
    bm = state.get_bookmarks()
    if not bm:
        console.print("[yellow]No bookmarks.[/]")
        return

    for aid, title in bm.items():
        console.print(f"\n[bold cyan]{title}[/] [dim]({aid})[/]")
        all_ep = _fetch_all_episodes(aid)
        if not all_ep:
            continue

        unwatched = [
            e
            for e in all_ep
            if not state.is_watched(aid, str(e.get("session", "")))
        ]

        if not unwatched:
            console.print("  [dim]All caught up![/]")
        else:
            for ep in unwatched[:10]:
                console.print(
                    f"  [yellow]Episode {ep.get('episode', '?')}[/]"
                    f"{': ' + ep['title'] if ep.get('title') else ''}"
                )
            remaining = len(unwatched) - 10
            if remaining > 0:
                console.print(f"  [dim]... and {remaining} more[/]")
