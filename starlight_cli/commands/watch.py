import json
import sys
from pathlib import Path

import click

from starlight_cli.cli import cli
from starlight_cli._helpers import _resolve_and_play


@cli.command()
@click.argument("anime")
@click.argument("episode_id", required=False)
@click.option("--episode", "-e", "episode_opt", default=None, help="Episode session ID (alternative to positional arg)")
def watch(anime, episode_id, episode_opt):
    ctx = click.get_current_context()
    if ctx.parent.obj.get("json"):
        from starlight_cli._helpers import _resolve_anime
        session_id, title = _resolve_anime(anime)
        sys.stdout.write(json.dumps({"session_id": session_id, "title": title}) + "\n")
        return
    _resolve_and_play(anime, episode_id or episode_opt, do_play=True)


@cli.command()
@click.argument("anime")
@click.argument("episode_id", required=False)
@click.option("--episode", "-e", "episode_opt", default=None, help="Episode session ID (alternative to positional arg)")
@click.option("--output", "-o", default=None, help="Output file (single) or directory (batch)")
@click.option("--batch", "-b", default=None, help="Download episode range (e.g. 1-10, 1,3,5)")
def download(anime, episode_id, episode_opt, output, batch):
    ctx = click.get_current_context()
    if ctx.parent.obj.get("json"):
        from starlight_cli._helpers import _resolve_anime
        session_id, title = _resolve_anime(anime)
        sys.stdout.write(json.dumps({"session_id": session_id, "title": title}) + "\n")
        return

    if batch:
        from starlight_cli._helpers import _parse_episode_range, _batch_download
        episodes = _parse_episode_range(batch)
        out_dir = Path(output) if output else None
        _batch_download(anime, episodes, out_dir)
    elif output:
        from starlight_cli._helpers import _resolve_and_download
        _resolve_and_download(anime, episode_id or episode_opt, output)
    else:
        _resolve_and_play(anime, episode_id or episode_opt, do_play=False)
