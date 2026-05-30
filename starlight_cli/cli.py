import click
from rich.console import Console

from starlight_cli.config import API_HEADERS

console = Console()
err_console = Console(stderr=True)


@click.group()
@click.option("--json", "json_output", is_flag=True, default=False, help="Output as JSON")
@click.pass_context
def cli(ctx, json_output):
    ctx.ensure_object(dict)["json"] = json_output
    if "YUhBIBrskG3DbXfMe7ZH" in API_HEADERS.get("Cookie", ""):
        err_console.print(
            "[yellow]Warning: Default cookies in use. They may expire.[/]"
        )


import starlight_cli.commands  # noqa: E402 — register commands via side-effect
