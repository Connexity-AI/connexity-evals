"""Shared Click context helpers."""

from typing import Any

import click

from cli.api_client import ApiClient


def root_obj(ctx: click.Context) -> dict[str, Any]:
    while ctx.parent is not None:
        ctx = ctx.parent
    obj = ctx.obj
    if not isinstance(obj, dict):
        raise click.ClickException("CLI context was not initialized.")
    return obj


def get_output_format(ctx: click.Context, override: str | None) -> str:
    base = root_obj(ctx)["output_format"]
    if not isinstance(base, str):
        raise click.ClickException("Invalid default output format.")
    fmt = override if override is not None else base
    if fmt not in ("json", "table"):
        raise click.BadParameter("output must be json or table")
    return fmt


def open_client(ctx: click.Context) -> ApiClient:
    o = root_obj(ctx)
    return ApiClient(base_url=o["api_url"], token=o["token"])
