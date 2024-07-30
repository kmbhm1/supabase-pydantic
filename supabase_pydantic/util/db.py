from typing import Any

import psycopg2

from supabase_pydantic.util.constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_CONSTRAINTS,
    GET_TABLE_COLUMN_DETAILS,
)
from supabase_pydantic.util.marshalers import construct_table_info


def create_connection(dbname: str, user: str, password: str, host: str, port: str) -> Any:
    """Create a connection to the database."""
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn


def check_connection(conn: Any) -> bool:
    """Check if the connection is open."""
    if conn.closed:
        print('PostGres connection is closed.')
        return False
    else:
        print('PostGres connection is open.')
        return True


def query_database(conn: Any, query: str) -> Any:
    """Query the database."""
    cur = conn.cursor()

    try:
        cur.execute(query)
        result = cur.fetchall()
        return result
    finally:
        cur.close()


def construct_table_info_from_postgres(
    db_name: str | None, user: str | None, password: str | None, host: str | None, port: str | None
) -> Any:
    """Construct table information from database."""
    # Get Table & Column details from the database
    conn: Any = None
    try:
        # Create a connection to the database & check if connection is successful
        assert (
            db_name is not None and user is not None and password is not None and host is not None and port is not None
        ), 'Environment variables not set correctly.'
        conn = create_connection(db_name, user, password, host, port)
        assert check_connection(conn)

        # Fetch table column details & foreign key details
        column_details = query_database(conn, GET_ALL_PUBLIC_TABLES_AND_COLUMNS)
        fk_details = query_database(conn, GET_TABLE_COLUMN_DETAILS)
        constraints = query_database(conn, GET_CONSTRAINTS)

        return construct_table_info(column_details, fk_details, constraints)
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()
            check_connection(conn)
