from typing import Any

import psycopg2


def create_connection(dbname: str, user: str, password: str, host: str, port: str) -> Any:
    """Create a connection to the database."""
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn


def check_connection(conn: Any) -> bool:
    """Check if the connection is open."""
    if conn.closed:
        print('Connection is closed.')
        return False
    else:
        print('Connection is open.')
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
