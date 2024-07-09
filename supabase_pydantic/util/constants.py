from enum import Enum


class RelationType(str, Enum):
    ONE_TO_ONE = 'One-to-One'
    ONE_TO_MANY = 'One-to-Many'
    MANY_TO_MANY = 'Many-to-Many'


class ModelGenerationType(str, Enum):
    PARENT = 'PARENT'
    MAIN = 'MAIN'


CUSTOM_MODEL_NAME = 'CustomModel'
CUSTOM_JSONAPI_META_MODEL_NAME = 'PydanticBaseModel'
BASE_CLASS_POSTFIX = 'BaseSchema'

CONSTRAINT_TYPE_MAP = {'p': 'PRIMARY KEY', 'f': 'FOREIGN KEY', 'u': 'UNIQUE', 'c': 'CHECK', 'x': 'EXCLUDE'}


PYDANTIC_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    'integer': ('int', None),
    'bigint': ('int', None),
    'smallint': ('int', None),
    'numeric': ('float', None),
    'text': ('str', None),
    'varchar': ('str', None),
    'character varying': ('str', None),
    'boolean': ('bool', None),
    'timestamp': ('datetime', 'from datetime import datetime'),
    'timestamp with time zone': ('datetime', 'from datetime import datetime'),
    'timestamp without time zone': ('datetime', 'from datetime import datetime'),
    'date': ('datetime.date', 'from datetime import date'),
    'uuid': ('UUID4', 'from pydantic import UUID4'),
    'json': ('dict | Json', 'from pydantic import Json'),
    'jsonb': ('dict | Json', 'from pydantic import Json'),
    'ARRAY': ('list', None),
    # Add more data types and their imports as necessary.
}


SQLALCHEMY_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    'integer': ('Integer', 'from sqlalchemy import Integer'),
    'bigint': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'smallint': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'numeric': ('Numeric', 'from sqlalchemy import Numeric'),
    'text': ('Text', 'from sqlalchemy import Text'),
    'varchar': ('String', 'from sqlalchemy import String'),
    'character varying': ('String', 'from sqlalchemy import String'),
    'boolean': ('Boolean', 'from sqlalchemy import Boolean'),
    'timestamp': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp with time zone': ('DateTime', 'from sqlalchemy.dialects.postgresql import TIMESTAMP'),
    'timestamp without time zone': ('DateTime', 'from sqlalchemy import DateTime'),
    'date': ('Date', 'from sqlalchemy import Date'),
    'uuid': ('UUID', 'from sqlalchemy.dialects.postgresql import UUID'),
    'json': ('JSON', 'from sqlalchemy import JSON'),
    'jsonb': ('JSONB', 'from sqlalchemy.dialects.postgresql import JSONB'),
    'ARRAY': ('ARRAY', 'from sqlalchemy.dialects.postgresql import ARRAY'),
    # Add more data types and their imports as necessary.
}


# Queries

GET_TABLE_COLUMN_DETAILS = """
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM
    information_schema.table_constraints AS tc
JOIN
    information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN
    information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public';
"""

GET_ALL_PUBLIC_TABLES_AND_COLUMNS = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.column_default,
    c.is_nullable,
    c.data_type,
    c.character_maximum_length,
    t.table_type
FROM
    information_schema.columns AS c
JOIN
    information_schema.tables AS t ON c.table_name = t.table_name AND c.table_schema = t.table_schema
WHERE
    c.table_schema = 'public'
    AND (t.table_type = 'BASE TABLE' OR t.table_type = 'VIEW')
ORDER BY
    c.table_schema, c.table_name, c.ordinal_position;
"""

GET_CONSTRAINTS = """
SELECT
    conname AS constraint_name,
    conrelid::regclass AS table_name,
    array_agg(a.attname) AS columns,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM
    pg_constraint
JOIN
    pg_attribute AS a ON a.attnum = ANY (conkey) AND a.attrelid = conrelid
WHERE
    connamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
GROUP BY
    conname, conrelid, contype, oid
ORDER BY
    conrelid::regclass::text, contype DESC;
"""
