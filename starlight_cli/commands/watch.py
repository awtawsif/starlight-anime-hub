import json

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
def download(anime, episode_id, episode_opt):
    ctx = click.get_current_context()
    if ctx.parent.obj.get("json"):
        from starlight_cli._helpers import _resolve_anime
        session_id, title = _resolve_anime(anime)
        sys.stdout.write(json.dumps({"session_id": session_id, "title": title}) + "\n")
        return
    _resolve_and_play(anime, episode_id or episode_opt, do_play=False)
