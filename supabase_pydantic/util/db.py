from typing import Any, Literal
from urllib.parse import urlparse

import psycopg2

from supabase_pydantic.util.constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_CONSTRAINTS,
    GET_TABLE_COLUMN_DETAILS,
    DatabaseConnectionType,
)
from supabase_pydantic.util.dataclasses import TableInfo
from supabase_pydantic.util.exceptions import ConnectionError
from supabase_pydantic.util.marshalers import construct_table_info


def query_database(conn: Any, query: str) -> Any:
    """Query the database."""
    cur = conn.cursor()

    try:
        cur.execute(query)
        result = cur.fetchall()
        return result
    finally:
        cur.close()


def create_connection(dbname: str, username: str, password: str, host: str, port: str) -> Any:
    """Create a connection to the database."""
    try:
        conn = psycopg2.connect(dbname=dbname, user=username, password=password, host=host, port=port)
        return conn
    except psycopg2.OperationalError as e:
        raise ConnectionError(f'Error connecting to database: {e}')


def create_connection_from_db_url(db_url: str) -> Any:
    """Create a connection to the database."""
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    host = result.hostname
    if result.port is None:
        raise ConnectionError(f'Invalid database URL port: {db_url}')
    port = str(result.port)

    assert username is not None, f'Invalid database URL user: {db_url}'
    assert password is not None, f'Invalid database URL pass: {db_url}'
    assert database is not None, f'Invalid database URL dbname: {db_url}'
    assert host is not None, f'Invalid database URL host: {db_url}'

    print(f'Connecting to database: {database} on host: {host} with user: {username} and port: {port}')

    return create_connection(database, username, password, host, port)


def check_connection(conn: Any) -> bool:
    """Check if the connection is open."""
    if conn.closed:
        print('PostGres connection is closed.')
        return False
    else:
        print('PostGres connection is open.')
        return True


class DBConnection:
    def __init__(self, conn_type: DatabaseConnectionType, **kwargs: Any) -> None:
        self.conn_type = conn_type
        self.kwargs = kwargs
        self.conn = self.create_connection()

    def create_connection(self) -> Any:
        """Get the connection to the database."""
        if self.conn_type == DatabaseConnectionType.DB_URL:
            return create_connection_from_db_url(self.kwargs['DB_URL'])
        elif self.conn_type == DatabaseConnectionType.LOCAL:
            try:
                return create_connection(
                    self.kwargs['DB_NAME'],
                    self.kwargs['DB_USER'],
                    self.kwargs['DB_PASS'],
                    self.kwargs['DB_HOST'],
                    self.kwargs['DB_PORT'],
                )
            except KeyError:
                raise ValueError('Invalid connection parameters.')
        else:
            raise ValueError('Invalid connection type.')

    def __enter__(self) -> Any:
        return self.conn

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        self.conn.close()
        return False


def construct_tables(conn_type: DatabaseConnectionType, **kwargs: Any) -> list[TableInfo]:
    """Construct table information from database."""
    assert kwargs, 'Invalid or empty connection parameters.'

    # Create a connection to the database & check if connection is successful
    with DBConnection(conn_type, **kwargs) as conn:
        assert check_connection(conn)

        try:
            # Fetch table column details & foreign key details
            column_details = query_database(conn, GET_ALL_PUBLIC_TABLES_AND_COLUMNS)
            fk_details = query_database(conn, GET_TABLE_COLUMN_DETAILS)
            constraints = query_database(conn, GET_CONSTRAINTS)

            return construct_table_info(column_details, fk_details, constraints)
        except Exception as e:
            raise e
