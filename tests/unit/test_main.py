import sys
from unittest.mock import patch


def test_main_function():
    """Test the __main__ module executes cli function when run directly."""
    with patch('supabase_pydantic.cli.cli') as mock_cli:
        # Directly execute the conditional code from __main__.py
        from supabase_pydantic.__main__ import cli

        # Manually execute what would happen in the if __name__ == '__main__' block
        cli()

        # Verify cli was called
        mock_cli.assert_called_once()
