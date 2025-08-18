"""Tests for database constants in supabase_pydantic.db.constants."""

import re

from supabase_pydantic.db.constants import POSTGRES_SQL_CONN_REGEX


import pytest


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.constants
def test_postgres_db_string_regex():
    """Test the regex for a postgres database string."""
    pattern = re.compile(POSTGRES_SQL_CONN_REGEX)

    assert pattern.match('postgresql://localhost')
    assert pattern.match('postgresql://localhost:5433')
    assert pattern.match('postgresql://localhost/mydb')
    assert pattern.match('postgresql://user@localhost')
    assert pattern.match('postgresql://user:secret@localhost')
    assert pattern.match('postgresql://other@localhost/otherdb?connect_timeout=10&application_name=myapp')
    assert not pattern.match('postgresql://host1:123,host2:456/somedb?application_name=myapp')
    assert pattern.match('postgres://myuser:mypassword@192.168.0.100:5432/mydatabase')
    assert pattern.match('postgresql://192.168.0.100/mydb')

    assert not pattern.match('postgresql://')
    assert not pattern.match('postgresql://localhost:')
    assert pattern.match('postgresql://localhost:5433/')
    assert pattern.match('postgresql://localhost:5433/mydb?')
    assert pattern.match('postgresql://localhost:5433/mydb?connect_timeout=10&application_name=myapp')
    assert pattern.match('postgresql://postgres:postgres@127.0.0.1:54333')
