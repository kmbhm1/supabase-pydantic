"""Tests for BaseDBConnector abstract class."""

import pytest
from unittest.mock import patch

from pydantic import BaseModel

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.models import DatabaseConnectionParams


class TestConnectionParams(DatabaseConnectionParams):
    """Test connection parameters model."""

    conn_type: str = 'test'
    host: str = 'localhost'
    port: int = 5432
    username: str = 'user'
    password: str = 'password'
    database: str = 'test_db'


class TestLegacyConnectionParams(BaseModel):
    """Legacy connection parameters model without to_dict method."""

    host: str = 'localhost'
    port: int = 5432
    username: str = 'user'
    password: str = 'password'
    database: str = 'test_db'

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'password': self.password,
            'database': self.database,
        }


class ConcreteDBConnector(BaseDBConnector[TestConnectionParams]):
    """Concrete implementation of BaseDBConnector for testing."""

    def connect(self, connection_params=None, **kwargs):
        """Implementation of abstract connect method."""
        return 'mock_connection'

    def check_connection(self, conn):
        """Implementation of abstract check_connection method."""
        return True if conn == 'mock_connection' else False

    def validate_connection_params(self, params):
        """Implementation of abstract validate_connection_params method."""
        if isinstance(params, dict):
            return TestConnectionParams(**params)
        return params

    def execute_query(self, conn, query, params=()):
        """Implementation of abstract execute_query method."""
        return [('result',)]

    def close_connection(self, conn):
        """Implementation of abstract close_connection method."""
        pass

    def get_url_connection_params(self, url):
        """Implementation of abstract get_url_connection_params method."""
        return {'host': 'localhost', 'port': 5432}


@pytest.mark.unit
@pytest.mark.db
class TestBaseDBConnector:
    """Tests for BaseDBConnector abstract class."""

    def test_init_with_pydantic_model(self):
        """Test initialization with a Pydantic model."""
        # Create params model
        params = TestConnectionParams(
            host='test-host', port=5433, username='test-user', password='test-password', database='test-database'
        )

        # Initialize connector
        connector = ConcreteDBConnector(params)

        # Check that parameters were set correctly
        assert connector.params_model == params
        assert connector.connection_params == {
            'conn_type': 'test',
            'host': 'test-host',
            'port': 5433,
            'username': 'test-user',
            'password': 'test-password',
            'database': 'test-database',
        }
        assert connector.connection is None

    def test_init_with_legacy_model(self):
        """Test initialization with a legacy model that uses to_dict method."""
        # Create params model
        params = TestLegacyConnectionParams(
            host='test-host', port=5433, username='test-user', password='test-password', database='test-database'
        )

        # Initialize connector
        connector = ConcreteDBConnector(params)

        # Check that parameters were set correctly
        assert connector.params_model == params
        assert connector.connection_params == {
            'host': 'test-host',
            'port': 5433,
            'username': 'test-user',
            'password': 'test-password',
            'database': 'test-database',
        }

    def test_init_with_dict(self):
        """Test initialization with a dictionary."""
        # Create params dict
        params = {
            'conn_type': 'test',
            'host': 'test-host',
            'port': 5433,
            'username': 'test-user',
            'password': 'test-password',
            'database': 'test-database',
        }

        # Initialize connector
        connector = ConcreteDBConnector(params)

        # Check that parameters were set correctly
        assert connector.params_model is None
        assert connector.connection_params == params

    def test_init_with_kwargs(self):
        """Test initialization with kwargs only."""
        # Initialize connector with kwargs
        connector = ConcreteDBConnector(
            conn_type='test',
            host='test-host',
            port=5433,
            username='test-user',
            password='test-password',
            database='test-database',
        )

        # Check that parameters were set correctly from kwargs
        assert connector.params_model is None
        assert connector.connection_params == {
            'conn_type': 'test',
            'host': 'test-host',
            'port': 5433,
            'username': 'test-user',
            'password': 'test-password',
            'database': 'test-database',
        }

    def test_init_with_empty_params(self):
        """Test initialization with no parameters."""
        # Initialize connector with no params
        connector = ConcreteDBConnector()

        # Check that parameters were set to empty dict
        assert connector.params_model is None
        assert connector.connection_params == {}

    @patch.object(ConcreteDBConnector, 'connect')
    @patch.object(ConcreteDBConnector, 'close_connection')
    def test_context_manager_with_model(self, mock_close, mock_connect):
        """Test context manager functionality with model parameters."""
        # Set up mock
        mock_connect.return_value = 'test_conn'

        # Create params model
        params = TestConnectionParams(
            host='test-host', port=5433, username='test-user', password='test-password', database='test-database'
        )

        # Use connector as context manager
        connector = ConcreteDBConnector(params)
        with connector as conn:
            assert conn == 'test_conn'
            assert connector.connection == 'test_conn'
            # Check that connect was called with model params
            mock_connect.assert_called_once_with(params)

        # Check that close was called
        mock_close.assert_called_once_with('test_conn')

    @patch.object(ConcreteDBConnector, 'connect')
    @patch.object(ConcreteDBConnector, 'close_connection')
    def test_context_manager_with_dict(self, mock_close, mock_connect):
        """Test context manager functionality with dict parameters."""
        # Set up mock
        mock_connect.return_value = 'test_conn'

        # Create params dict
        params = {
            'conn_type': 'test',
            'host': 'test-host',
            'port': 5433,
            'username': 'test-user',
            'password': 'test-password',
            'database': 'test-database',
        }

        # Use connector as context manager
        connector = ConcreteDBConnector(params)
        with connector as conn:
            assert conn == 'test_conn'
            assert connector.connection == 'test_conn'
            # Check that connect was called with dict params
            mock_connect.assert_called_once_with(params)

        # Check that close was called
        mock_close.assert_called_once_with('test_conn')

    @patch.object(ConcreteDBConnector, 'connect')
    def test_context_manager_with_exception(self, mock_connect):
        """Test context manager handling of exceptions."""
        # Set up mock
        mock_connect.return_value = 'test_conn'

        # Use connector as context manager with an exception
        connector = ConcreteDBConnector()
        try:
            with connector:
                raise ValueError('Test exception')
        except ValueError as e:
            # Exception should be propagated
            assert str(e) == 'Test exception'

        # Check that connection was set
        assert connector.connection == 'test_conn'


@pytest.mark.unit
@pytest.mark.db
class TestAbstractMethodsDBConnector:
    """Tests for abstract methods of BaseDBConnector."""

    def setup_method(self):
        """Set up method to create a minimal concrete subclass."""

        class MinimalDBConnector(BaseDBConnector):
            pass

        self.MinimalDBConnector = MinimalDBConnector

    def test_abstract_methods(self):
        """Test that abstract methods raise TypeError when not implemented."""
        with pytest.raises(TypeError) as excinfo:
            # This should raise because we can't instantiate with abstract methods
            _ = self.MinimalDBConnector()

        # Check that the error message mentions the abstract methods
        assert 'abstract methods' in str(excinfo.value)
        # Check that it mentions some of the abstract methods
        abstract_methods = [
            'check_connection',
            'connect',
            'execute_query',
            'close_connection',
            'get_url_connection_params',
            'validate_connection_params',
        ]
        for method in abstract_methods:
            assert method in str(excinfo.value)

    def test_partial_implementation(self):
        """Test that partial implementation still requires all abstract methods."""

        # Create a class that implements some but not all abstract methods
        class PartialDBConnector(BaseDBConnector):
            def connect(self, connection_params=None, **kwargs):
                return 'mock_connection'

            def check_connection(self, conn):
                return True

            # Missing other abstract methods

        with pytest.raises(TypeError) as excinfo:
            _ = PartialDBConnector()

        # Check that the error mentions the missing abstract methods
        assert 'abstract methods' in str(excinfo.value)
        # Should mention some of these missing methods
        missing_methods = [
            'execute_query',
            'close_connection',
            'get_url_connection_params',
            'validate_connection_params',
        ]
        assert any(method in str(excinfo.value) for method in missing_methods)
