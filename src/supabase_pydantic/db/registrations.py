"""Database component registrations for the factory."""

import logging

from supabase_pydantic.db.connectors.mysql.connector import MySQLConnector
from supabase_pydantic.db.connectors.mysql.schema_reader import MySQLSchemaReader
from supabase_pydantic.db.connectors.postgres.connector import PostgresConnector
from supabase_pydantic.db.connectors.postgres.schema_reader import PostgresSchemaReader
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factory import DatabaseFactory
from supabase_pydantic.db.marshalers.mysql.column import MySQLColumnMarshaler
from supabase_pydantic.db.marshalers.mysql.constraints import MySQLConstraintMarshaler
from supabase_pydantic.db.marshalers.mysql.relationship import MySQLRelationshipMarshaler
from supabase_pydantic.db.marshalers.mysql.schema import MySQLSchemaMarshaler
from supabase_pydantic.db.marshalers.postgres.column import PostgresColumnMarshaler
from supabase_pydantic.db.marshalers.postgres.constraints import PostgresConstraintMarshaler
from supabase_pydantic.db.marshalers.postgres.relationship import PostgresRelationshipMarshaler
from supabase_pydantic.db.marshalers.postgres.schema import PostgresSchemaMarshaler

# Get Logger
logger = logging.getLogger(__name__)


def register_database_components() -> None:
    """Register all database components with the factory."""
    # Register PostgreSQL components
    logger.debug('Registering PostgreSQL components with factory')
    DatabaseFactory.register_connector(DatabaseType.POSTGRES, PostgresConnector)
    DatabaseFactory.register_schema_reader(DatabaseType.POSTGRES, PostgresSchemaReader)
    DatabaseFactory.register_column_marshaler(DatabaseType.POSTGRES, PostgresColumnMarshaler)
    DatabaseFactory.register_constraint_marshaler(DatabaseType.POSTGRES, PostgresConstraintMarshaler)
    DatabaseFactory.register_relationship_marshaler(DatabaseType.POSTGRES, PostgresRelationshipMarshaler)
    DatabaseFactory.register_schema_marshaler(DatabaseType.POSTGRES, PostgresSchemaMarshaler)

    # Register MySQL components
    logger.debug('Registering MySQL components with factory')
    DatabaseFactory.register_connector(DatabaseType.MYSQL, MySQLConnector)
    DatabaseFactory.register_schema_reader(DatabaseType.MYSQL, MySQLSchemaReader)
    DatabaseFactory.register_column_marshaler(DatabaseType.MYSQL, MySQLColumnMarshaler)
    DatabaseFactory.register_constraint_marshaler(DatabaseType.MYSQL, MySQLConstraintMarshaler)
    DatabaseFactory.register_relationship_marshaler(DatabaseType.MYSQL, MySQLRelationshipMarshaler)
    DatabaseFactory.register_schema_marshaler(DatabaseType.MYSQL, MySQLSchemaMarshaler)

    # TODO: Add other database types as needed

    logger.debug('Database components registered with factory')
