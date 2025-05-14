import logging
import pprint
from typing import Any

import toml

from src.supabase_pydantic.db.constants import AppConfig, ToolConfig

# Pretty print for testing
pp = pprint.PrettyPrinter(indent=4)

# Standard choices
model_choices = ['pydantic']
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


def load_config() -> AppConfig:
    """Load the configuration from the pyproject.toml file."""
    try:
        with open('pyproject.toml') as f:
            config_data: dict[str, Any] = toml.load(f)
            tool_config: ToolConfig = config_data.get('tool', {})
            app_config: AppConfig = tool_config.get('supabase_pydantic', {})
            return app_config
    except FileNotFoundError:
        return {}


config_dict: AppConfig = load_config()
