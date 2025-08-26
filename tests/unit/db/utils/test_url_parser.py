"""Tests for the URL parser module."""

import pytest

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.utils.url_parser import detect_database_type, get_database_name_from_url


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.utils
class TestDatabaseTypeDetection:
    """Tests for database type detection from URLs."""

    @pytest.mark.parametrize(
        'db_url, expected_type',
        [
            ('postgresql://user:pass@localhost:5432/testdb', DatabaseType.POSTGRES),
            ('postgres://user:pass@localhost:5432/testdb', DatabaseType.POSTGRES),
            ('postgresql://localhost/testdb', DatabaseType.POSTGRES),
            ('postgresql://localhost:5432/testdb?sslmode=require', DatabaseType.POSTGRES),
            ('mysql://user:pass@localhost:3306/testdb', DatabaseType.MYSQL),
            ('mariadb://user:pass@localhost:3306/testdb', DatabaseType.MYSQL),
            ('mysql://localhost/testdb', DatabaseType.MYSQL),
            ('mysql://localhost:3306/testdb?charset=utf8mb4', DatabaseType.MYSQL),
        ],
    )
    def test_detect_database_type_valid(self, db_url, expected_type):
        """Test detection of database types from valid URLs."""
        result = detect_database_type(db_url)
        assert result == expected_type, f'Failed to detect {expected_type} from {db_url}'

    @pytest.mark.parametrize(
        'db_url',
        [
            '',
            None,
            'sqlite:///path/to/db.sqlite',
            'mongodb://localhost:27017',
            'oracle://user:pass@localhost:1521/testdb',
            'invalid_url',
            'http://example.com',
        ],
    )
    def test_detect_database_type_invalid(self, db_url):
        """Test handling of invalid or unsupported URLs."""
        result = detect_database_type(db_url)
        assert result is None, f'Expected None for {db_url}, got {result}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.utils
class TestDatabaseNameExtraction:
    """Tests for extracting database names from URLs."""

    @pytest.mark.parametrize(
        'db_url, expected_name',
        [
            ('postgresql://user:pass@localhost:5432/testdb', 'testdb'),
            ('postgres://user:pass@localhost/mydatabase', 'mydatabase'),
            ('mysql://user:pass@localhost:3306/production_db', 'production_db'),
            ('postgresql://localhost/test-db-name', 'test-db-name'),
            ('mysql://localhost/db_with_underscores', 'db_with_underscores'),
            ('postgresql://user:pass@localhost:5432/testdb?sslmode=require', 'testdb'),
        ],
    )
    def test_get_database_name_valid(self, db_url, expected_name):
        """Test extracting database names from valid URLs."""
        result = get_database_name_from_url(db_url)
        assert result == expected_name, f'Failed to extract db name from {db_url}'

    @pytest.mark.parametrize(
        'db_url',
        [
            '',
            None,
            'postgresql://localhost',
            'mysql://localhost:3306',
            'invalid_url',
            'postgresql://',
            'http://example.com',
        ],
    )
    def test_get_database_name_invalid(self, db_url):
        """Test handling of invalid URLs or URLs without database names."""
        result = get_database_name_from_url(db_url)
        assert result is None, f'Expected None for {db_url}, got {result}'
