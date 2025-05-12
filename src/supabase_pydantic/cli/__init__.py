"""CLI module for supabase-pydantic package."""

from typing import Any

import toml

from src.supabase_pydantic.core.utils import check_readiness
from src.supabase_pydantic.utils.constants import AppConfig, ToolConfig

from .main import cli


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


__all__ = [
    'check_readiness',
    'cli',
    'load_config',
]
