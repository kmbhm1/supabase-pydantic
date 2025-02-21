import os
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

STD_PYDANTIC_FILENAME = 'schemas.py'
STD_SQLALCHEMY_FILENAME = 'database.py'
STD_SEED_DATA_FILENAME = 'seed.sql'


class WriterClassType(Enum):
    """Enum for writer class types."""

    BASE = 'base'  # The main Row model with all fields
    BASE_WITH_PARENT = 'base_with_parent'
    PARENT = 'parent'
    INSERT = 'insert'  # Model for insert operations - auto-generated fields optional
    UPDATE = 'update'  # Model for update operations - all fields optional


class DatabaseConnectionType(Enum):
    """Enum for database connection types."""

    LOCAL = 'local'
    DB_URL = 'db_url'


class AppConfig(TypedDict, total=False):
    default_directory: str
    overwrite_existing_files: bool
    nullify_base_schema: bool


class ToolConfig(TypedDict):
    supabase_pydantic: AppConfig


class OrmType(Enum):
    """Enum for file types."""

    PYDANTIC = 'pydantic'
    SQLALCHEMY = 'sqlalchemy'


class FrameWorkType(Enum):
    """Enum for framework types."""

    FASTAPI = 'fastapi'


@dataclass
class WriterConfig:
    file_type: OrmType
    framework_type: FrameWorkType
    filename: str
    directory: str
    enabled: bool

    def ext(self) -> str:
        """Get the file extension based on the file name."""
        return self.filename.split('.')[-1]

    def name(self) -> str:
        """Get the file name without the extension."""
        return self.filename.split('.')[0]

    def fpath(self) -> str:
        """Get the full file path."""
        return os.path.join(self.directory, self.filename)

    def to_dict(self) -> dict[str, str]:
        """Convert the WriterConfig object to a dictionary."""
        return {
            'file_type': str(self.file_type),
            'framework_type': str(self.framework_type),
            'filename': self.filename,
            'directory': self.directory,
            'enabled': str(self.enabled),
        }


class RelationType(str, Enum):
    ONE_TO_ONE = 'One-to-One'
    ONE_TO_MANY = 'One-to-Many'
    MANY_TO_MANY = 'Many-to-Many'
    MANY_TO_ONE = 'Many-to-One'  # When a table has a foreign key to another table (e.g., File -> Project)


class ModelGenerationType(str, Enum):
    PARENT = 'PARENT'
    MAIN = 'MAIN'


class DatabaseUserDefinedType(str, Enum):
    DOMAIN = 'DOMAIN'
    COMPOSITE = 'COMPOSITE'
    ENUM = 'ENUM'
    RANGE = 'RANGE'


CUSTOM_MODEL_NAME = 'CustomModel'
BASE_CLASS_POSTFIX = 'BaseSchema'

CONSTRAINT_TYPE_MAP = {'p': 'PRIMARY KEY', 'f': 'FOREIGN KEY', 'u': 'UNIQUE', 'c': 'CHECK', 'x': 'EXCLUDE'}
USER_DEFINED_TYPE_MAP = {'d': 'DOMAIN', 'c': 'COMPOSITE', 'e': 'ENUM', 'r': 'RANGE'}

PYDANTIC_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    'integer': ('int', None),
    'bigint': ('int', None),
    'smallint': ('int', None),
    'numeric': ('float', None),
    'decimal': ('float', None),
    'real': ('float', None),
    'double precision': ('float', None),
    'serial': ('int', None),
    'bigserial': ('int', None),
    'money': ('Decimal', 'from decimal import Decimal'),
    'character varying': ('str', None),
    'character varying(n)': ('str', None),
    'varchar(n)': ('str', None),
    'character(n)': ('str', None),
    'char(n)': ('str', None),
    'text': ('str', None),
    'bytea': ('bytes', None),
    'timestamp': ('datetime.datetime', 'import datetime'),
    'timestamp with time zone': ('datetime.datetime', 'import datetime'),
    'timestamp without time zone': ('datetime.datetime', 'import datetime'),
    'date': ('datetime.date', 'import datetime'),
    'time': ('datetime.time', 'import datetime'),
    'time with time zone': ('datetime.time', 'import datetime'),
    'interval': ('timedelta', 'from datetime import timedelta'),
    'boolean': ('bool', None),
    'enum': ('str', None),  # Enums need specific handling depending on their defined values
    'point': ('Tuple[float, float]', 'from typing import Tuple'),
    'line': ('Any', 'from typing import Any'),  # Special geometric types may need custom handling
    'lseg': ('Any', 'from typing import Any'),
    'box': ('Any', 'from typing import Any'),
    'path': ('Any', 'from typing import Any'),
    'polygon': ('Any', 'from typing import Any'),
    'circle': ('Any', 'from typing import Any'),
    'cidr': ('IPv4Network', 'from ipaddress import IPv4Network, IPv6Network'),
    'inet': ('IPv4Address | IPv6Address', 'from ipaddress import IPv4Address, IPv6Address'),
    'macaddr': ('str', None),
    'macaddr8': ('str', None),
    'bit': ('str', None),
    'bit varying': ('str', None),
    'tsvector': ('str', None),
    'tsquery': ('str', None),
    'uuid': ('UUID4', 'from pydantic import UUID4'),
    'xml': ('str', None),
    'json': ('dict | Json', 'from pydantic import Json'),
    'jsonb': ('dict | Json', 'from pydantic import Json'),
    'ARRAY': ('list', None),  # Generic list; specify further based on the array's element type
}


SQLALCHEMY_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    'integer': ('Integer', 'from sqlalchemy import Integer'),
    'bigint': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'smallint': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'numeric': ('Numeric', 'from sqlalchemy import Numeric'),
    'decimal': ('Numeric', 'from sqlalchemy import Numeric'),
    'real': ('Float', 'from sqlalchemy import Float'),
    'double precision': ('Float', 'from sqlalchemy import Float'),
    'serial': ('Integer', 'from sqlalchemy import Integer'),  # Auto increment in context
    'bigserial': ('BigInteger', 'from sqlalchemy import BigInteger'),  # Auto increment in context
    'money': ('Numeric', 'from sqlalchemy import Numeric'),  # No specific Money type in SQLAlchemy
    'character varying': ('String', 'from sqlalchemy import String'),
    'character varying(n)': ('String', 'from sqlalchemy import String'),
    'varchar(n)': ('String', 'from sqlalchemy import String'),
    'character(n)': ('String', 'from sqlalchemy import String'),
    'char(n)': ('String', 'from sqlalchemy import String'),
    'text': ('Text', 'from sqlalchemy import Text'),
    'bytea': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'timestamp': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp with time zone': ('DateTime', 'from sqlalchemy.dialects.postgresql import TIMESTAMP'),
    'timestamp without time zone': ('DateTime', 'from sqlalchemy import DateTime'),
    'date': ('Date', 'from sqlalchemy import Date'),
    'time': ('Time', 'from sqlalchemy import Time'),
    'time with time zone': ('Time', 'from sqlalchemy.dialects.postgresql import TIME'),
    'interval': ('Interval', 'from sqlalchemy import Interval'),
    'boolean': ('Boolean', 'from sqlalchemy import Boolean'),
    'enum': ('Enum', 'from sqlalchemy import Enum'),  # Enums need specific handling based on defined values
    'point': ('PickleType', 'from sqlalchemy import PickleType'),  # No direct mapping, custom handling
    'line': ('PickleType', 'from sqlalchemy import PickleType'),
    'lseg': ('PickleType', 'from sqlalchemy import PickleType'),
    'box': ('PickleType', 'from sqlalchemy import PickleType'),
    'path': ('PickleType', 'from sqlalchemy import PickleType'),
    'polygon': ('PickleType', 'from sqlalchemy import PickleType'),
    'circle': ('PickleType', 'from sqlalchemy import PickleType'),
    'cidr': ('CIDR', 'from sqlalchemy.dialects.postgresql import CIDR'),
    'inet': ('INET', 'from sqlalchemy.dialects.postgresql import INET'),
    'macaddr': ('MACADDR', 'from sqlalchemy.dialects.postgresql import MACADDR'),
    'macaddr8': ('MACADDR8', 'from sqlalchemy.dialects.postgresql import MACADDR8'),
    'bit': ('BIT', 'from sqlalchemy.dialects.postgresql import BIT'),
    'bit varying': ('BIT', 'from sqlalchemy.dialects.postgresql import BIT'),
    'tsvector': ('TSVECTOR', 'from sqlalchemy.dialects.postgresql import TSVECTOR'),
    'tsquery': ('TSQUERY', 'from sqlalchemy.dialects.postgresql import TSQUERY'),
    'uuid': ('UUID', 'from sqlalchemy.dialects.postgresql import UUID'),
    'xml': ('Text', 'from sqlalchemy import Text'),  # XML handled as Text for simplicity
    'json': ('JSON', 'from sqlalchemy import JSON'),
    'jsonb': ('JSONB', 'from sqlalchemy.dialects.postgresql import JSONB'),
    'ARRAY': ('ARRAY', 'from sqlalchemy.dialects.postgresql import ARRAY'),  # Generic ARRAY; specify further
}


SQLALCHEMY_V2_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    'integer': ('Integer,int', 'from sqlalchemy import Integer'),
    'bigint': ('BigInteger,int', 'from sqlalchemy import BigInteger'),
    'smallint': ('SmallInteger,int', 'from sqlalchemy import SmallInteger'),
    'numeric': ('Numeric,float', 'from sqlalchemy import Numeric'),
    'decimal': ('Numeric,float', 'from sqlalchemy import Numeric'),
    'real': ('Float,float', 'from sqlalchemy import Float'),
    'double precision': ('Float,float', 'from sqlalchemy import Float'),
    'serial': ('Integer,int', 'from sqlalchemy import Integer'),  # Auto increment in context
    'bigserial': ('BigInteger,int', 'from sqlalchemy import BigInteger'),  # Auto increment in context
    'money': (
        'Numeric,Decimal',
        'from sqlalchemy import Numeric\nfrom decimal import Decimal',
    ),  # No specific Money type in SQLAlchemy
    'character varying': ('String,str', 'from sqlalchemy import String'),
    'character varying(n)': ('String,str', 'from sqlalchemy import String'),
    'varchar(n)': ('String,str', 'from sqlalchemy import String'),
    'character(n)': ('String,str', 'from sqlalchemy import String'),
    'char(n)': ('String,str', 'from sqlalchemy import String'),
    'text': ('Text,str', 'from sqlalchemy import Text'),
    'bytea': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    'timestamp': ('DateTime,datetime', 'from sqlalchemy import DateTime\nfrom datetime import datetime'),
    'timestamp with time zone': (
        'DateTime,datetime',
        'from sqlalchemy.dialects.postgresql import TIMESTAMP\nfrom datetime import datetime',
    ),
    'timestamp without time zone': (
        'DateTime,datetime',
        'from sqlalchemy import DateTime\nfrom datetime import datetime',
    ),
    'date': ('Date,date', 'from sqlalchemy import Date\nfrom datetime import date'),
    'time': ('Time,time', 'from sqlalchemy import Time\nfrom datetime import time'),
    'time with time zone': (
        'Time,datetime.time',
        'from sqlalchemy.dialects.postgresql import TIME\nfrom datetime import time',
    ),
    'interval': ('Interval,timedelta', 'from sqlalchemy import Interval\nfrom datetime import timedelta'),
    'boolean': ('Boolean,bool', 'from sqlalchemy import Boolean'),
    'enum': ('Enum,str', 'from sqlalchemy import Enum'),  # Enums need specific handling based on defined values
    'point': (
        'PickleType,Tuple[float, float]',
        'from sqlalchemy import PickleType\nfrom typeing import Tuple',
    ),  # No direct mapping, custom handling
    'line': ('PickleType,Any', 'from sqlalchemy import PickleType\nfrom typing import Any'),
    'lseg': ('PickleType,Any', 'from sqlalchemy import PickleType\nfrom typing import Any'),
    'box': ('PickleType,Any', 'from sqlalchemy import PickleType\nfrom typing import Any'),
    'path': ('PickleType,Any', 'from sqlalchemy import PickleType\nfrom typing import Any'),
    'polygon': ('PickleType,Any', 'from sqlalchemy import PickleType\nfrom typing import Any'),
    'circle': ('PickleType,Any', 'from sqlalchemy import PickleType\nfrom typing import Any'),
    'cidr': (
        'CIDR,IPv4Network',
        'from sqlalchemy.dialects.postgresql import CIDR\nfrom ipaddress import IPv4Network',
    ),
    'inet': (
        'INET,IPv4Address | IPv6Address',
        'from sqlalchemy.dialects.postgresql import INET\nfrom ipaddress import IPv4Address, IPv6Address',
    ),
    'macaddr': ('MACADDR,str', 'from sqlalchemy.dialects.postgresql import MACADDR'),
    'macaddr8': ('MACADDR8,str', 'from sqlalchemy.dialects.postgresql import MACADDR8'),
    'bit': ('BIT,str', 'from sqlalchemy.dialects.postgresql import BIT'),
    'bit varying': ('BIT,str', 'from sqlalchemy.dialects.postgresql import BIT'),
    'tsvector': ('TSVECTOR,str', 'from sqlalchemy.dialects.postgresql import TSVECTOR'),
    'tsquery': ('TSQUERY,str', 'from sqlalchemy.dialects.postgresql import TSQUERY'),
    'uuid': ('UUID,UUID4', 'from sqlalchemy.dialects.postgresql import UUID\nfrom pydantic import UUID4'),
    'xml': ('Text,str', 'from sqlalchemy import Text'),  # XML handled as Text for simplicity
    'json': ('JSON,dict | Json', 'from sqlalchemy import JSON\nfrom pydantic import Json'),
    'jsonb': ('JSONB,dict | Json', 'from sqlalchemy.dialects.postgresql import JSONB\nfrom pydantic import Json'),
    'ARRAY': ('ARRAY,list', 'from sqlalchemy.dialects.postgresql import ARRAY'),  # Generic ARRAY; specify further
}


# Queries

TABLES_QUERY = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema = %s
"""

COLUMNS_QUERY = """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = %s AND table_name = %s
"""

SCHEMAS_QUERY = """
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
"""

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
    AND tc.table_schema = %s;
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
    t.table_type,
    c.identity_generation
FROM
    information_schema.columns AS c
JOIN
    information_schema.tables AS t ON c.table_name = t.table_name AND c.table_schema = t.table_schema
WHERE
    c.table_schema = %s
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
    connamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
GROUP BY
    conname, conrelid, contype, oid
ORDER BY
    conrelid::regclass::text, contype DESC;
"""

GET_USER_DEFINED_TYPES = """
SELECT typname AS type_name,
       typnamespace::regnamespace AS namespace,
       typowner::regrole AS owner,
       typcategory AS category,
       typisdefined AS is_defined,
       typtype AS type,
       typinput::regproc AS input_function,
       typoutput::regproc AS output_function,
       typreceive::regproc AS receive_function,
       typsend::regproc AS send_function,
       typlen AS length,
       typbyval AS by_value,
       typalign AS alignment,
       typdelim AS delimiter,
       typrelid::regclass AS related_table,
       typelem::regtype AS element_type,
       typcollation::regcollation AS collation
FROM pg_type
WHERE typtype IN ('d', 'c', 'e', 'r')  -- d: domain, c: composite, e: enum, r: range
ORDER BY typnamespace, typname;
"""

GET_ENUM_TYPES = """
SELECT t.typname AS type_name,
       t.typnamespace::regnamespace AS namespace,
       t.typowner::regrole AS owner,
       t.typcategory AS category,
       t.typisdefined AS is_defined,
       t.typtype AS type,
       array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
FROM pg_type t
LEFT JOIN pg_enum e ON t.oid = e.enumtypid
WHERE t.typtype IN ('d', 'c', 'e', 'r')
GROUP BY t.typname, t.typnamespace, t.typowner, t.typcategory, t.typisdefined, t.typtype
ORDER BY t.typnamespace, t.typname;
"""

GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING = """
SELECT a.attname AS column_name,
       c.relname AS table_name,
       t.typnamespace::regnamespace AS namespace,
       t.typname AS type_name,
       t.typtype AS type_category,
       CASE t.typtype
         WHEN 'd' THEN 'Domain'
         WHEN 'c' THEN 'Composite'
         WHEN 'e' THEN 'Enum'
         WHEN 'r' THEN 'Range'
         ELSE 'Other'
       END AS type_description
FROM pg_attribute a
JOIN pg_class c ON a.attrelid = c.oid
JOIN pg_type t ON a.atttypid = t.oid
WHERE c.relkind = 'r' -- Only look at ordinary tables
  AND NOT a.attisdropped; -- Skip dropped (deleted) columns
"""


# Regex

POSTGRES_SQL_CONN_REGEX = (
    r'(postgresql|postgres)://([^:@\s]*(?::[^@\s]*)?@)?(?P<server>[^/\?\s:]+)(:\d+)?(/[^?\s]*)?(\?[^\s]*)?$'
)
