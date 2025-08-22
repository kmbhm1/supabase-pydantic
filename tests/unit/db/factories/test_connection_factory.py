"""Tests for the connection parameter factory."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factories.connection_factory import ConnectionParamFactory
from supabase_pydantic.db.models import PostgresConnectionParams, MySQLConnectionParams


@pytest.mark.unit
@pytest.mark.db
class TestConnectionParamFactory:
    """Tests for the ConnectionParamFactory class."""

    def test_create_postgres_explicit(self):
        """Test creating PostgreSQL connection params with explicit DB type."""
        params = {'host': 'localhost', 'port': '5432', 'dbname': 'testdb', 'user': 'user', 'password': 'pass'}
        result = ConnectionParamFactory.create_connection_params(params, db_type=DatabaseType.POSTGRES)

        assert isinstance(result, PostgresConnectionParams)
        assert result.host == 'localhost'
        assert result.port == '5432'
        assert result.dbname == 'testdb'
        assert result.user == 'user'
        assert result.password == 'pass'

    def test_create_mysql_explicit(self):
        """Test creating MySQL connection params with explicit DB type."""
        params = {'host': 'localhost', 'port': '3306', 'dbname': 'testdb', 'user': 'user', 'password': 'pass'}
        result = ConnectionParamFactory.create_connection_params(params, db_type=DatabaseType.MYSQL)

        assert isinstance(result, MySQLConnectionParams)
        assert result.host == 'localhost'
        assert result.port == '3306'
        assert result.dbname == 'testdb'
        assert result.user == 'user'
        assert result.password == 'pass'

    def test_default_to_postgres(self):
        """Test default to PostgreSQL when no DB type is provided."""
        params = {'host': 'localhost', 'port': '5432', 'dbname': 'testdb', 'user': 'user', 'password': 'pass'}
        result = ConnectionParamFactory.create_connection_params(params)

        assert isinstance(result, PostgresConnectionParams)
        assert result.host == 'localhost'

    @patch('supabase_pydantic.db.factories.connection_factory.detect_database_type')
    def test_autodetect_postgres_from_url(self, mock_detect):
        """Test auto-detection of PostgreSQL from db_url."""
        mock_detect.return_value = DatabaseType.POSTGRES

        params = {'db_url': 'postgresql://user:pass@localhost:5432/testdb'}
        result = ConnectionParamFactory.create_connection_params(params)

        assert isinstance(result, PostgresConnectionParams)
        assert result.db_url == 'postgresql://user:pass@localhost:5432/testdb'
        mock_detect.assert_called_once_with('postgresql://user:pass@localhost:5432/testdb')

    @patch('supabase_pydantic.db.factories.connection_factory.detect_database_type')
    def test_autodetect_mysql_from_url(self, mock_detect):
        """Test auto-detection of MySQL from db_url."""
        mock_detect.return_value = DatabaseType.MYSQL

        params = {'db_url': 'mysql://user:pass@localhost:3306/testdb'}
        result = ConnectionParamFactory.create_connection_params(params)

        assert isinstance(result, MySQLConnectionParams)
        assert result.db_url == 'mysql://user:pass@localhost:3306/testdb'
        mock_detect.assert_called_once_with('mysql://user:pass@localhost:3306/testdb')

    @patch('supabase_pydantic.db.factories.connection_factory.detect_database_type')
    def test_autodetect_fallback_to_postgres(self, mock_detect):
        """Test fallback to PostgreSQL when auto-detection returns None."""
        # Simulate detect_database_type returning None (unable to identify DB type)
        mock_detect.return_value = None

        # Even though this is a valid PostgreSQL URL, we're testing the behavior
        # when the detection mechanism fails to identify the type
        params = {'db_url': 'postgresql://user:pass@localhost:5432/testdb'}
        result = ConnectionParamFactory.create_connection_params(params)

        assert isinstance(result, PostgresConnectionParams)
        assert result.db_url == 'postgresql://user:pass@localhost:5432/testdb'
        mock_detect.assert_called_once_with('postgresql://user:pass@localhost:5432/testdb')

    def test_unsupported_db_type(self):
        """Test error handling for unsupported DB types."""
        params = {'host': 'localhost', 'dbname': 'testdb'}

        # Create a custom enum value that isn't supported
        unsupported_type = 'UNSUPPORTED'

        with pytest.raises(ValueError) as excinfo:
            ConnectionParamFactory.create_connection_params(params, db_type=unsupported_type)

        assert 'Unsupported database type' in str(excinfo.value)
