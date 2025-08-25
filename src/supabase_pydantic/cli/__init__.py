"""Command line interface for Supabase Pydantic."""

from typing import Any

import click

from supabase_pydantic.cli.commands.clean import clean
from supabase_pydantic.cli.commands.gen import gen
from supabase_pydantic.utils.logging import setup_logging


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: Any) -> None:
    """A CLI tool for generating Pydantic models from a Supabase/PostgreSQL database.

    In the future, more ORM frameworks and databases will be supported. In the works:
    Django, REST Flask, SQLAlchemy, Tortoise-ORM, and more.

    Additionally, more REST API generators will be supported ...

    Stay tuned!
    """
    # Initialize logging globally (defaults to INFO). Individual commands may
    # reconfigure (e.g., --debug) if needed.
    setup_logging('INFO')

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    # When invoked without a subcommand, just show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


# Register commands
cli.add_command(clean)
cli.add_command(gen)

if __name__ == '__main__':
    cli()
