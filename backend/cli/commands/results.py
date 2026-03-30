"""List runs and show run details."""

import sys
from typing import Any

import click

from cli import output
from cli.context import get_output_format, open_client, root_obj


@click.group("results")
def results_group() -> None:
    """Inspect eval run results."""


@results_group.command("list")
@click.option("--status", default=None, help="Filter by run status")
@click.option("--limit", default=100, type=int, show_default=True)
@click.option("--skip", default=0, type=int, show_default=True)
@click.option(
    "--output",
    "output_override",
    type=click.Choice(["json", "table"]),
    default=None,
)
@click.pass_context
def results_list(
    ctx: click.Context,
    status: str | None,
    limit: int,
    skip: int,
    output_override: str | None,
) -> None:
    """List recent runs."""
    if not root_obj(ctx).get("token"):
        raise click.ClickException(
            "Authentication required: set CONNEXITY_EVALS_API_TOKEN or pass --token."
        )
    fmt = get_output_format(ctx, output_override)
    params: dict[str, Any] = {"limit": limit, "skip": skip}
    if status:
        params["status"] = status

    with open_client(ctx) as client:
        data = client.list_runs(params=params)
    output.emit(data, output_format=fmt)


@results_group.command("show")
@click.argument("run_id")
@click.option(
    "--output",
    "output_override",
    type=click.Choice(["json", "table"]),
    default=None,
)
@click.pass_context
def results_show(
    ctx: click.Context,
    run_id: str,
    output_override: str | None,
) -> None:
    """Show one run with aggregate metrics."""
    if not root_obj(ctx).get("token"):
        raise click.ClickException(
            "Authentication required: set CONNEXITY_EVALS_API_TOKEN or pass --token."
        )
    fmt = get_output_format(ctx, output_override)

    with open_client(ctx) as client:
        run = client.get_run(run_id)

    if fmt == "json":
        output.emit(run, output_format="json")
    else:
        click.echo(output.format_run_detail(run))

    final = str(run.get("status", "")).lower()
    if final in ("failed", "cancelled"):
        sys.exit(1)
