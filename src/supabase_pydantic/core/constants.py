"""Constants and configuration types for supabase-pydantic."""

import os
from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

# Standard filenames
STD_PYDANTIC_FILENAME = 'schemas.py'
STD_SQLALCHEMY_FILENAME = 'database.py'
STD_SEED_DATA_FILENAME = 'seed.sql'

# Constants for model generation
CUSTOM_MODEL_NAME = 'CustomModel'
BASE_CLASS_POSTFIX = 'BaseSchema'

# Type mapping dictionaries
CONSTRAINT_TYPE_MAP = {'p': 'PRIMARY KEY', 'f': 'FOREIGN KEY', 'u': 'UNIQUE', 'c': 'CHECK', 'x': 'EXCLUDE'}
USER_DEFINED_TYPE_MAP = {'d': 'DOMAIN', 'c': 'COMPOSITE', 'e': 'ENUM', 'r': 'RANGE'}


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
    """Enum for relationship types between tables."""

    ONE_TO_ONE = 'One-to-One'
    ONE_TO_MANY = 'One-to-Many'
    MANY_TO_MANY = 'Many-to-Many'
    MANY_TO_ONE = 'Many-to-One'  # When a table has a foreign key to another table (e.g., File -> Project)


class ModelGenerationType(str, Enum):
    """Enum for model generation types."""

    PARENT = 'PARENT'
    MAIN = 'MAIN'


class DatabaseUserDefinedType(str, Enum):
    """Enum for database user-defined types."""

    DOMAIN = 'DOMAIN'
    COMPOSITE = 'COMPOSITE'
    ENUM = 'ENUM'
    RANGE = 'RANGE'


# PostgreSQL to Python/Pydantic type mapping
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
    'point': ('tuple[float, float]', 'from typing import Tuple'),
    'line': ('Any', 'from typing import Any'),  # Special geometric types may need custom handling
    'lseg': ('Any', 'from typing import Any'),
    'box': ('Any', 'from typing import Any'),
    'path': ('Any', 'from typing import Any'),
    'polygon': ('Any', 'from typing import Any'),
    'circle': ('Any', 'from typing import Any'),
    'cidr': ('str', None),
    'inet': ('str', None),
    'macaddr': ('str', None),
    'bit': ('str', None),
    'bit varying': ('str', None),
    'tsvector': ('str', None),
    'tsquery': ('str', None),
    'uuid': ('UUID', 'from uuid import UUID'),
    'xml': ('str', None),
    'json': ('dict | list | str', 'from typing import Any, Dict, List'),
    'jsonb': ('dict | list | str', 'from typing import Any, Dict, List'),
    'int4range': ('tuple[int, int]', 'from typing import Tuple'),
    'int8range': ('tuple[int, int]', 'from typing import Tuple'),
    'numrange': ('tuple[float, float]', 'from typing import Tuple'),
    'tsrange': ('tuple[datetime.datetime, datetime.datetime]', 'import datetime\nfrom typing import Tuple'),
    'tstzrange': ('tuple[datetime.datetime, datetime.datetime]', 'import datetime\nfrom typing import Tuple'),
    'daterange': ('tuple[datetime.date, datetime.date]', 'import datetime\nfrom typing import Tuple'),
    'hstore': ('dict[str, str]', 'from typing import Dict'),
    'ltree': ('str', None),
    'array': ('list', 'from typing import List'),
}

# SQLAlchemy type mapping (placeholder - used in the original code)
SQLALCHEMY_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    'integer': ('Integer', 'from sqlalchemy import Integer'),
    'bigint': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'smallint': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'numeric': ('Numeric', 'from sqlalchemy import Numeric'),
    'decimal': ('Numeric', 'from sqlalchemy import Numeric'),
    'real': ('Float', 'from sqlalchemy import Float'),
    'double precision': ('Float', 'from sqlalchemy import Float'),
    'serial': ('Integer', 'from sqlalchemy import Integer'),
    'bigserial': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'money': ('Numeric', 'from sqlalchemy import Numeric'),
    'character varying': ('String', 'from sqlalchemy import String'),
    'character varying(n)': ('String', 'from sqlalchemy import String'),
    'varchar(n)': ('String', 'from sqlalchemy import String'),
    'character(n)': ('String', 'from sqlalchemy import String'),
    'char(n)': ('String', 'from sqlalchemy import String'),
    'text': ('Text', 'from sqlalchemy import Text'),
    'bytea': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'timestamp': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp with time zone': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp without time zone': ('DateTime', 'from sqlalchemy import DateTime'),
    'date': ('Date', 'from sqlalchemy import Date'),
    'time': ('Time', 'from sqlalchemy import Time'),
    'time with time zone': ('Time', 'from sqlalchemy import Time'),
    'interval': ('Interval', 'from sqlalchemy import Interval'),
    'boolean': ('Boolean', 'from sqlalchemy import Boolean'),
    'enum': ('Enum', 'from sqlalchemy import Enum'),
    'uuid': ('UUID', 'from sqlalchemy import UUID'),
    'json': ('JSON', 'from sqlalchemy import JSON'),
    'jsonb': ('JSONB', 'from sqlalchemy import JSONB'),
}
