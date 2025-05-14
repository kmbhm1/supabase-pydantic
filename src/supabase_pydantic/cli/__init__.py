from typing import Any

import click
from dotenv import find_dotenv, load_dotenv

# Import commands
from src.supabase_pydantic.cli.commands import clean, gen

# Re-export functions and classes - making them directly accessible as if they were defined here
# This is needed to support the test patching approach
from src.supabase_pydantic.core.writers.factories import FileWriterFactory
from src.supabase_pydantic.db.connection import construct_tables
from src.supabase_pydantic.utils.config import get_standard_jobs
from src.supabase_pydantic.utils.io import get_working_directories

# Define what's available for import from this module
__all__ = [
    'cli',
    'clean',
    'gen',
    'construct_tables',
    'get_working_directories',
    'get_standard_jobs',
    'FileWriterFactory',
]

# Load environment variables from .env file
load_dotenv(find_dotenv())


@click.group()
@click.pass_context
def cli(ctx: Any) -> None:
    """A CLI tool for generating Pydantic models from a Supabase/PostgreSQL database.

    In the future, more ORM frameworks and databases will be supported. In the works:
    Django, REST Flask, SQLAlchemy, Tortoise-ORM, and more.

    Additionally, more REST API generators will be supported ...

    Stay tuned!
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)


# Register commands
cli.add_command(clean)
cli.add_command(gen)


if __name__ == '__main__':
    cli()  # keep; for testing & debugging  # noqa
