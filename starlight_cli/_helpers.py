import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.table import Table
from rich.prompt import Prompt
from rich.markup import escape

from starlight_cli.cli import console, err_console
from starlight_cli import state
from starlight_cli.api import (
    fetch_anime_details,
    fetch_anime_search_results,
    fetch_episode_list,
    fetch_episode_streams,
)
from starlight_cli.kwik import extract_hls_url
from starlight_cli.player import play

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
        alnum = re.sub(r"[^a-zA-Z0-9]", "", title)
        if not alnum:
            return None
        base = alnum[:4].lower()
    elif len(words) == 1:
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
        err_console.print(f"[red]Error resolving UUID:[/] {error}")
        sys.exit(1)

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


def _fetch_all_episodes(session_id: str, sort: str = "episode_asc", max_pages: int = 50):
    first_batch, pagination, error = fetch_episode_list(session_id, 1, sort)
    if error:
        err_console.print(f"[red]{error}[/]")
        return []
    all_ep = list(first_batch)
    last_page = min(pagination.get("last_page", 1), max_pages)
    if last_page <= 1:
        return all_ep

    with ThreadPoolExecutor(max_workers=4) as pool:
        fut_map = {
            pool.submit(fetch_episode_list, session_id, p, sort): p
            for p in range(2, last_page + 1)
        }
        for fut in as_completed(fut_map):
            batch, _, err = fut.result()
            if not err:
                all_ep.extend(batch)
    return all_ep


def _pick_episode(session_id: str):
    with console.status("Fetching episodes..."):
        all_ep = _fetch_all_episodes(session_id)
    if not all_ep:
        err_console.print("[red]No episodes found for this anime.[/]")
        sys.exit(1)

    console.print(f"[dim]Episodes 1–{len(all_ep)} available[/]")

    while True:
        display_eps = all_ep[-30:]
        table = Table()
        table.add_column("#", style="cyan")

        for ep in display_eps:
            table.add_row(str(ep.get("episode", "?")))

        if len(all_ep) > 30:
            console.print(f"[dim]Showing last 30 of {len(all_ep)} episodes[/]")
        console.print(table)

        choice = Prompt.ask("Enter episode number or range (e.g. 1-50)")

        range_match = re.match(r"^(\d+)-(\d+)$", choice)
        if range_match:
            start, end = int(range_match.group(1)), int(range_match.group(2))
            filtered = [e for e in all_ep if start <= int(e.get("episode", 0)) <= end]
            if not filtered:
                err_console.print(f"[red]No episodes in range {start}-{end}.[/]")
                continue
            t = Table()
            t.add_column("#", style="cyan")
            for ep in filtered:
                t.add_row(str(ep.get("episode", "?")))
            console.print(t)
            sub = Prompt.ask("Enter episode number")
            matched = [e for e in filtered if str(e.get("episode")) == sub]
            if matched:
                return matched[0].get("session")
            err_console.print(f"[red]Episode {sub} not found in range.[/]")
            continue

        matched = [e for e in all_ep if str(e.get("episode")) == choice]
        if matched:
            return matched[0].get("session")
        err_console.print(f"[red]Episode {choice} not found.[/]")


def _pick_quality(items: list[dict]) -> dict:
    if len(items) == 1:
        return items[0]

    from collections import OrderedDict

    groups = OrderedDict()
    for i, item in enumerate(items):
        audio = item.get('audio', 'unknown')
        fansub = item.get('fansub', '')
        groups.setdefault((audio, fansub), []).append((i + 1, item))

    console.print("\n[bold]Available qualities:[/]")
    for (audio, fansub), group in groups.items():
        parts = [f"[{audio or '?'}]"]
        if fansub:
            parts.append(fansub)
        header = escape(" ".join(parts))
        console.print(f"  [bold]{header}:[/]")
        for idx, item in group:
            console.print(f"    {idx}. {item.get('resolution', '?')}p")

    choice = Prompt.ask(
        "Select",
        choices=[str(i) for i in range(1, len(items) + 1)],
    )
    return items[int(choice) - 1]


def _resolve_and_play(anime: str, episode_id: str | None, do_play: bool):
    session_id, _ = _resolve_anime(anime)

    if not episode_id:
        episode_id = _pick_episode(session_id)

    with console.status("Fetching streams..."):
        streams, error = fetch_episode_streams(session_id, episode_id)

    if error:
        err_console.print(f"[red]{error}[/]")
        sys.exit(1)
    if not streams:
        err_console.print("[red]No streams found.[/]")
        sys.exit(1)

    selected = _pick_quality(streams)
    kwik_url = selected["kwik_url"]

    with console.status("Extracting video URL..."):
        try:
            video_url = extract_hls_url(kwik_url)
        except Exception as e:
            err_console.print(f"[red]Failed to extract video URL:[/] {e}")
            sys.exit(1)

    if do_play:
        label = f"{selected.get('resolution', '?')}p"
        console.print(f"[green]Streaming {label}...[/]")
        play(video_url)
    else:
        console.print(f"\n[bold green]Video URL:[/] {video_url}")
