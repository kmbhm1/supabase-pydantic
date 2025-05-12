"""Command-line interface for supabase-pydantic."""

from typing import Any

import click
from dotenv import find_dotenv, load_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Standard choices
model_choices = ['pydantic']
framework_choices = ['fastapi']


@click.group()
@click.pass_context
def cli(ctx: Any) -> None:
    """A CLI tool for generating Pydantic models from database schemas.

    Currently supports PostgreSQL/Supabase with plans to add support for:
    - MySQL
    - SQLite
    - SQL Server
    and more.

    Additionally, more frameworks beyond FastAPI will be supported in the future.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)


# Import command modules here to avoid circular imports
# We'll implement these modules next
from src.supabase_pydantic.cli.commands.clean import clean  # noqa
from src.supabase_pydantic.cli.commands.generate import gen  # noqa

# Register commands with the CLI group
cli.add_command(clean)
cli.add_command(gen)


if __name__ == '__main__':
    # This allows for direct execution during development
    cli()  # pragma: no cover
