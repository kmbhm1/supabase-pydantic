"""Tests for BaseSchemaReader abstract class."""

import pytest
from unittest.mock import MagicMock

from supabase_pydantic.db.abstract.base_schema_reader import BaseSchemaReader


class TestBaseSchemaReader:
    """Tests for BaseSchemaReader abstract class."""

    def test_init(self):
        """Test initialization."""
        mock_connector = MagicMock()

        # We can't instantiate the abstract class directly, so create a concrete subclass
        class ConcreteSchemaReader(BaseSchemaReader):
            def get_schemas(self, conn):
                return ['schema1', 'schema2']

            def get_tables(self, conn, schema):
                return [('table1',)]

            def get_columns(self, conn, schema):
                return [('table1', 'column1', 'integer')]

            def get_foreign_keys(self, conn, schema):
                return [('table1', 'column1', 'table2', 'id')]

            def get_constraints(self, conn, schema):
                return [('table1', 'pk_table1', 'p')]

            def get_user_defined_types(self, conn, schema):
                return [('enum_type', 'ENUM', ['val1', 'val2'])]

            def get_type_mappings(self, conn, schema):
                return [('table1', 'column1', 'enum_type')]

        # Create an instance
        schema_reader = ConcreteSchemaReader(mock_connector)

        # Check that connector was set correctly
        assert schema_reader.connector == mock_connector


class TestAbstractMethods:
    """Tests for abstract methods of BaseSchemaReader."""

    def setup_method(self):
        """Set up method to create a minimal concrete subclass that doesn't implement all methods."""

        class MinimalSchemaReader(BaseSchemaReader):
            pass

        self.MinimalSchemaReader = MinimalSchemaReader
        self.mock_connector = MagicMock()

    def test_abstract_get_schemas(self):
        """Test that get_schemas is abstract and raises NotImplementedError."""
        with pytest.raises(TypeError) as excinfo:
            # This should raise because we can't instantiate with abstract methods
            _ = self.MinimalSchemaReader(self.mock_connector)

        # Check that the error message mentions the abstract methods
        assert 'abstract methods' in str(excinfo.value)
        assert 'get_schemas' in str(excinfo.value)

    def test_concrete_implementation(self):
        """Test that concrete implementation works."""

        # Create a concrete implementation
        class ConcreteReader(BaseSchemaReader):
            def get_schemas(self, conn):
                return ['schema1']

            def get_tables(self, conn, schema):
                return [('table1',)]

            def get_columns(self, conn, schema):
                return [('table1', 'column1', 'integer')]

            def get_foreign_keys(self, conn, schema):
                return [('table1', 'column1', 'table2', 'id')]

            def get_constraints(self, conn, schema):
                return [('table1', 'pk_table1', 'p')]

            def get_user_defined_types(self, conn, schema):
                return [('enum_type', 'ENUM', ['val1', 'val2'])]

            def get_type_mappings(self, conn, schema):
                return [('table1', 'column1', 'enum_type')]

        # Should not raise
        reader = ConcreteReader(self.mock_connector)

        # Check that methods can be called
        mock_conn = MagicMock()
        schemas = reader.get_schemas(mock_conn)
        assert schemas == ['schema1']

        tables = reader.get_tables(mock_conn, 'schema1')
        assert tables == [('table1',)]

        columns = reader.get_columns(mock_conn, 'schema1')
        assert columns == [('table1', 'column1', 'integer')]

        foreign_keys = reader.get_foreign_keys(mock_conn, 'schema1')
        assert foreign_keys == [('table1', 'column1', 'table2', 'id')]

        constraints = reader.get_constraints(mock_conn, 'schema1')
        assert constraints == [('table1', 'pk_table1', 'p')]

        user_defined_types = reader.get_user_defined_types(mock_conn, 'schema1')
        assert user_defined_types == [('enum_type', 'ENUM', ['val1', 'val2'])]

        type_mappings = reader.get_type_mappings(mock_conn, 'schema1')
        assert type_mappings == [('table1', 'column1', 'enum_type')]


class TestPartialImplementation:
    """Tests for partial implementation of BaseSchemaReader."""

    def test_partial_implementation(self):
        """Test that partial implementation still requires all abstract methods."""

        # Create a class that implements some but not all abstract methods
        class PartialReader(BaseSchemaReader):
            def get_schemas(self, conn):
                return ['schema1']

            def get_tables(self, conn, schema):
                return [('table1',)]

            # Missing other abstract methods

        with pytest.raises(TypeError) as excinfo:
            _ = PartialReader(MagicMock())

        # Check that the error mentions the missing abstract methods
        assert 'abstract methods' in str(excinfo.value)
        assert any(
            method in str(excinfo.value)
            for method in [
                'get_columns',
                'get_foreign_keys',
                'get_constraints',
                'get_user_defined_types',
                'get_type_mappings',
            ]
        )
