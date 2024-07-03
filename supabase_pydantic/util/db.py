from typing import Any
import psycopg2


def create_connection(dbname, user, password, host, port):
    """Create a connection to the database."""
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn


def check_connection(conn):
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
