"""Supabase Pydantic - Generate Pydantic models from database schemas."""

__version__ = '0.1.0'  # This should match the version in pyproject.toml

# Re-export key components for easier imports
# CLI entry point
from src.supabase_pydantic.cli.main import cli
from src.supabase_pydantic.db import AdapterFactory, DatabaseAdapter, DatabaseType

__all__ = [
    'AdapterFactory',
    'DatabaseAdapter',
    'DatabaseType',
    'cli',
]
