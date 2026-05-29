import re
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from starlight_cli.api import (
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

UUID_RE = re.compile(r"^[a-f0-9-]{36}$")


def _slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def _is_uuid(s: str) -> bool:
    return bool(UUID_RE.match(s))


def _generate_code(title: str, existing: set) -> str | None:
    words = re.findall(r"[a-zA-Z]+", title)
    if not words:
        return None

    if len(words) == 1:
        base = words[0][:4].lower()
    else:
        base = (words[0][:2] + words[1][:2]).lower()

    if base not in existing:
        return base

    n = 2
    while f"{base}{n}" in existing:
        n += 1
    return f"{base}{n}"


def _assign_code(title: str, session_id: str) -> str | None:
    existing_code = state.get_session_code(session_id)
    if existing_code:
        return existing_code

    existing = set(state.get_all_codes().keys())
    code = _generate_code(title, existing)
    if not code:
        return None

    state.save_code(code, session_id, title)
    return code


def _resolve_anime(identifier: str):
    info = state.get_code_info(identifier)
    if info:
        return info["session_id"], info["title"]

    if _is_uuid(identifier):
        details, error = fetch_anime_details(identifier)
        if not error:
            title = details.get("title", identifier)
            return identifier, title

    results, error = fetch_anime_search_results(identifier)
    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not results:
        err_console.print(
            f"[red]Could not resolve '{identifier}'. Try searching first.[/]"
        )
        sys.exit(1)

    slug_map = {_slugify(r["title"]): r for r in results}
    if identifier in slug_map:
        r = slug_map[identifier]
        return r["session"], r["title"]

    if len(results) == 1:
        r = results[0]
        return r["session"], r["title"]

    console.print("[yellow]Multiple matches. Pick one:[/]")
    for i, r in enumerate(results, 1):
        console.print(f"  {i}. {r['title']} [dim]({r.get('year', '')})[/]")
    choice = Prompt.ask(
        "Select", choices=[str(i) for i in range(1, len(results) + 1)]
    )
    r = results[int(choice) - 1]
    return r["session"], r["title"]


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

    for ep in all_ep:
        table.add_row(
            str(ep.get("episode", "?")),
            ep.get("title", "") or "",
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


def _resolve_and_play(anime: str, episode_id: str | None, do_play: bool):
    session_id, _ = _resolve_anime(anime)

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


@cli.command()
@click.argument("anime")
def detail(anime):
    session_id, title = _resolve_anime(anime)
    details, error = fetch_anime_details(session_id)
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
            for item in items:
                t.add_row(item.get("title", "N/A"), item.get("type", "N/A"))
            console.print(t)


@cli.command()
@click.argument("anime")
@click.option("--page", default=1, type=int)
@click.option(
    "--sort",
    default="episode_asc",
    type=click.Choice(["episode_asc", "episode_desc"]),
)
def episodes(anime, page, sort):
    session_id, title = _resolve_anime(anime)

    batch, pagination, error = fetch_episode_list(session_id, page, sort)
    if error:
        err_console.print(f"[red]Error:[/] {error}")
        sys.exit(1)

    if not batch:
        console.print("[yellow]No episodes found.[/]")
        return

    cur = pagination.get("current_page", 1)
    last = pagination.get("last_page", 1)

    table = Table(title=f"{title}  —  Episodes (page {cur}/{last})")
    table.add_column("#", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Duration")
    table.add_column("Filler")

    for ep in batch:
        table.add_row(
            str(ep.get("episode", "")),
            ep.get("title", "N/A") or "",
            str(ep.get("duration", "")),
            "[red]Yes[/]" if ep.get("filler") else "",
        )

    console.print(table)


@cli.command()
@click.argument("anime")
@click.argument("episode_id", required=False)
def watch(anime, episode_id):
    _resolve_and_play(anime, episode_id, do_play=True)


@cli.command()
@click.argument("anime")
@click.argument("episode_id", required=False)
def download(anime, episode_id):
    _resolve_and_play(anime, episode_id, do_play=False)


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
    table.add_column("Code", style="cyan", width=6)
    table.add_column("Title", style="white")

    for aid, title in bm.items():
        code = state.get_session_code(aid) or ""
        table.add_row(code, title)

    console.print(table)


@bookmarks.command()
@click.argument("anime")
def add(anime):
    session_id, title = _resolve_anime(anime)
    bm = state.get_bookmarks()
    if session_id in bm:
        console.print("[yellow]Already bookmarked.[/]")
        return

    state.add_bookmark(session_id, title)
    _assign_code(title, session_id)
    code = state.get_session_code(session_id) or ""
    console.print(f"[green]Bookmarked:[/] {title} [dim]({code})[/]")


@bookmarks.command()
@click.argument("anime")
def remove(anime):
    session_id, title = _resolve_anime(anime)
    bm = state.get_bookmarks()
    if session_id not in bm:
        console.print("[yellow]Not bookmarked.[/]")
        return
    state.remove_bookmark(session_id)
    console.print(f"[green]Removed bookmark:[/] {title}")


@cli.command()
def continue_watching():
    bm = state.get_bookmarks()
    if not bm:
        console.print("[yellow]No bookmarks.[/]")
        return

    for aid, title in bm.items():
        code = state.get_session_code(aid) or ""
        console.print(
            f"\n[bold cyan]{title}[/] [dim]({code})[/]"
            if code
            else f"\n[bold cyan]{title}[/]"
        )
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
