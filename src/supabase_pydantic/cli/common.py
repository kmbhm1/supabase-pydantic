import logging
from collections.abc import Callable
from typing import Any

import click
import toml

from supabase_pydantic.utils.constants import AppConfig, ToolConfig

# Standard choices
model_choices = ['pydantic', 'sqlalchemy']
framework_choices = ['fastapi']


def check_readiness(env_vars: dict[str, str | None]) -> bool:
    """Check if environment variables are set correctly."""
    if not env_vars:
        logging.error('No environment variables provided.')
        return False
    for k, v in env_vars.items():
        logging.debug(f'Checking environment variable: {k}')
        if v is None:
            logging.error(f'Environment variables not set correctly. {k} is missing. Please set it in .env file.')
            return False

    logging.debug('All required environment variables are set')
    return True


def load_config(config_path: str | None = None) -> AppConfig:
    """Load the configuration from pyproject.toml or specified config file."""
    if config_path:
        # Load from specified config file
        try:
            with open(config_path) as f:
                # Handle YAML files if that's what you use
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    import yaml

                    return yaml.safe_load(f)
                # Handle TOML files
                elif config_path.endswith('.toml'):
                    return toml.load(f).get('tool', {}).get('supabase_pydantic', {})
        except FileNotFoundError:
            click.echo(f'Config file not found: {config_path}')
            return {}
    else:
        # Default to pyproject.toml
        try:
            with open('pyproject.toml') as f:
                config_data: dict[str, Any] = toml.load(f)
                tool_config: ToolConfig = config_data.get('tool', {})
                app_config: AppConfig = tool_config.get('supabase_pydantic', {})
                return app_config
        except FileNotFoundError:
            return {}


# Common option groups and decorators
def common_options(f: Callable) -> Callable:
    """Common options for CLI commands."""
    decorators = [
        click.option('--config', '-c', help='Path to config file.'),
        # Add other common options here
    ]

    # Apply all decorators
    for decorator in reversed(decorators):
        f = decorator(f)
    return f
