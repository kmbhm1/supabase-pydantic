"""Factory for creating database-specific components."""

from typing import Any, TypeVar

from pydantic import BaseModel

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.abstract.base_schema_reader import BaseSchemaReader
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.marshalers.abstract.base_column_marshaler import BaseColumnMarshaler
from supabase_pydantic.db.marshalers.abstract.base_constraint_marshaler import BaseConstraintMarshaler
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.marshalers.abstract.base_schema_marshaler import BaseSchemaMarshaler

T = TypeVar('T', bound=BaseModel)


class DatabaseFactory:
    """Factory for creating database-specific components."""

    _connector_registry: dict[DatabaseType, type[BaseDBConnector[Any]]] = {}
    _schema_reader_registry: dict[DatabaseType, type[BaseSchemaReader]] = {}
    _column_marshaler_registry: dict[DatabaseType, type[BaseColumnMarshaler]] = {}
    _constraint_marshaler_registry: dict[DatabaseType, type[BaseConstraintMarshaler]] = {}
    _relationship_marshaler_registry: dict[DatabaseType, type[BaseRelationshipMarshaler]] = {}
    _schema_marshaler_registry: dict[DatabaseType, type[BaseSchemaMarshaler]] = {}

    @classmethod
    def register_connector(cls, db_type: DatabaseType, connector_class: type[BaseDBConnector[Any]]) -> None:
        """Register a connector class for a specific database type.

        Args:
            db_type: Database type enum value.
            connector_class: Connector implementation class.
        """
        cls._connector_registry[db_type] = connector_class

    @classmethod
    def register_schema_reader(cls, db_type: DatabaseType, schema_reader_class: type[BaseSchemaReader]) -> None:
        """Register a schema reader class for a specific database type.

        Args:
            db_type: Database type enum value.
            schema_reader_class: Schema reader implementation class.
        """
        cls._schema_reader_registry[db_type] = schema_reader_class

    @classmethod
    def register_column_marshaler(
        cls, db_type: DatabaseType, column_marshaler_class: type[BaseColumnMarshaler]
    ) -> None:
        """Register a column marshaler class for a specific database type.

        Args:
            db_type: Database type enum value.
            column_marshaler_class: Column marshaler implementation class.
        """
        cls._column_marshaler_registry[db_type] = column_marshaler_class

    @classmethod
    def register_constraint_marshaler(
        cls, db_type: DatabaseType, constraint_marshaler_class: type[BaseConstraintMarshaler]
    ) -> None:
        """Register a constraint marshaler class for a specific database type.

        Args:
            db_type: Database type enum value.
            constraint_marshaler_class: Constraint marshaler implementation class.
        """
        cls._constraint_marshaler_registry[db_type] = constraint_marshaler_class

    @classmethod
    def register_relationship_marshaler(
        cls, db_type: DatabaseType, relationship_marshaler_class: type[BaseRelationshipMarshaler]
    ) -> None:
        """Register a relationship marshaler class for a specific database type.

        Args:
            db_type: Database type enum value.
            relationship_marshaler_class: Relationship marshaler implementation class.
        """
        cls._relationship_marshaler_registry[db_type] = relationship_marshaler_class

    @classmethod
    def register_schema_marshaler(
        cls, db_type: DatabaseType, schema_marshaler_class: type[BaseSchemaMarshaler]
    ) -> None:
        """Register a schema marshaler class for a specific database type.

        Args:
            db_type: Database type enum value.
            schema_marshaler_class: Schema marshaler implementation class.
        """
        cls._schema_marshaler_registry[db_type] = schema_marshaler_class

    @classmethod
    def create_connector(
        cls, db_type: DatabaseType, connection_params: BaseModel | dict[str, Any] | None = None, **kwargs: Any
    ) -> BaseDBConnector[Any]:
        """Create a connector instance for the specified database type.

        Args:
            db_type: Database type enum value.
            connection_params: Connection parameters as a Pydantic model or dictionary.
            **kwargs: Additional arguments to pass to the connector constructor.

        Returns:
            Connector instance.

        Raises:
            ValueError: If no connector is registered for the database type.
        """
        connector_class = cls._connector_registry.get(db_type)
        if not connector_class:
            raise ValueError(f'No connector registered for database type: {db_type}')

        # Pass connection parameters separately to leverage the new Pydantic model support
        return connector_class(connection_params=connection_params, **kwargs)

    @classmethod
    def create_schema_reader(
        cls, db_type: DatabaseType, connector: BaseDBConnector[Any] | None = None, **kwargs: Any
    ) -> BaseSchemaReader:
        """Create a schema reader instance for the specified database type.

        Args:
            db_type: Database type enum value.
            connector: Optional connector instance to use. If not provided,
                       a new connector will be created.
            **kwargs: Additional arguments to pass to the schema reader constructor.

        Returns:
            Schema reader instance.

        Raises:
            ValueError: If no schema reader is registered for the database type.
        """
        schema_reader_class = cls._schema_reader_registry.get(db_type)
        if not schema_reader_class:
            raise ValueError(f'No schema reader registered for database type: {db_type}')

        if not connector:
            connector = cls.create_connector(db_type)

        return schema_reader_class(connector, **kwargs)

    @classmethod
    def create_marshalers(cls, db_type: DatabaseType, **kwargs: Any) -> BaseSchemaMarshaler:
        """Create marshaler instances for the specified database type.

        Args:
            db_type: Database type enum value.
            **kwargs: Additional arguments to pass to the marshalers' constructors.

        Returns:
            Schema marshaler instance with appropriate component marshalers.

        Raises:
            ValueError: If any required marshaler is not registered for the database type.
        """
        column_marshaler_class = cls._column_marshaler_registry.get(db_type)
        if not column_marshaler_class:
            raise ValueError(f'No column marshaler registered for database type: {db_type}')

        constraint_marshaler_class = cls._constraint_marshaler_registry.get(db_type)
        if not constraint_marshaler_class:
            raise ValueError(f'No constraint marshaler registered for database type: {db_type}')

        relationship_marshaler_class = cls._relationship_marshaler_registry.get(db_type)
        if not relationship_marshaler_class:
            raise ValueError(f'No relationship marshaler registered for database type: {db_type}')

        schema_marshaler_class = cls._schema_marshaler_registry.get(db_type)
        if not schema_marshaler_class:
            raise ValueError(f'No schema marshaler registered for database type: {db_type}')

        column_marshaler = column_marshaler_class(**kwargs)
        constraint_marshaler = constraint_marshaler_class(**kwargs)
        relationship_marshaler = relationship_marshaler_class(**kwargs)

        return schema_marshaler_class(column_marshaler, constraint_marshaler, relationship_marshaler, **kwargs)
