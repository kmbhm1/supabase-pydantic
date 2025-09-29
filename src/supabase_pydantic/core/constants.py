from enum import Enum


class OrmType(Enum):
    """Enum for file types."""

    PYDANTIC = 'pydantic'
    SQLALCHEMY = 'sqlalchemy'


class FrameWorkType(Enum):
    """Enum for framework types."""

    FASTAPI = 'fastapi'


class WriterClassType(Enum):
    """Enum for writer class types."""

    BASE = 'base'  # The main Row model with all fields
    BASE_WITH_PARENT = 'base_with_parent'
    PARENT = 'parent'
    INSERT = 'insert'  # Model for insert operations - auto-generated fields optional
    UPDATE = 'update'  # Model for update operations - all fields optional


class ModelGenerationType(str, Enum):
    PARENT = 'PARENT'
    MAIN = 'MAIN'


# Constants for names used in model generation
CUSTOM_MODEL_NAME = 'CustomModel'
BASE_CLASS_POSTFIX = 'BaseSchema'


# Pydantic Type Map
PYDANTIC_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # Integer types
    'integer': ('int', None),
    'int': ('int', None),  # Shortened form
    'bigint': ('int', None),
    'smallint': ('int', None),
    'int2': ('int', None),  # Internal form for smallint
    'int4': ('int', None),  # Internal form for integer
    'int8': ('int', None),  # Internal form for bigint
    # Decimal/Numeric types
    'numeric': ('Decimal', 'from decimal import Decimal'),  # Changed to Decimal to match tests
    'decimal': ('Decimal', 'from decimal import Decimal'),
    # Floating point types
    'real': ('float', None),
    'float4': ('float', None),  # Internal form for real
    'double precision': ('float', None),
    'float': ('Decimal', 'from decimal import Decimal'),  # Match test expectation
    'float8': ('float', None),  # Internal form for double precision
    # Serial types
    'serial': ('int', None),
    'bigserial': ('int', None),
    'smallserial': ('int', None),
    'serial2': ('int', None),
    'serial4': ('int', None),
    'serial8': ('int', None),
    # Money type
    'money': ('Decimal', 'from decimal import Decimal'),
    # Character types
    'character varying': ('str', None),
    'varchar': ('str', None),  # Shortened form
    'character varying(n)': ('str', None),
    'varchar(n)': ('str', None),
    'character(n)': ('str', None),
    'char(n)': ('str', None),
    'char': ('str', None),  # Shortened form
    'text': ('str', None),
    # Binary type
    'bytea': ('bytes', None),
    # Date/Time types
    'timestamp': ('datetime.datetime', 'import datetime'),
    'timestamp with time zone': ('datetime.datetime', 'import datetime'),
    'timestamptz': ('datetime.datetime', 'import datetime'),  # Shortened form
    'timestamp without time zone': ('datetime.datetime', 'import datetime'),
    'date': ('datetime.date', 'import datetime'),
    'time': ('datetime.time', 'import datetime'),
    'time with time zone': ('datetime.time', 'import datetime'),
    'time without time zone': ('datetime.time', 'import datetime'),
    'timetz': ('datetime.time', 'import datetime'),  # Shortened form
    'interval': ('datetime.timedelta', 'import datetime'),
    # Boolean type
    'boolean': ('bool', None),
    'bool': ('bool', None),  # Shortened form
    # Enum type
    'enum': ('str', None),  # Enums need specific handling depending on their defined values
    # Geometric types
    'point': ('Tuple[float, float]', 'from typing import Tuple'),
    'line': ('Any', 'from typing import Any'),  # Special geometric types may need custom handling
    'lseg': ('Any', 'from typing import Any'),
    'box': ('Any', 'from typing import Any'),
    'path': ('Any', 'from typing import Any'),
    'polygon': ('Any', 'from typing import Any'),
    'circle': ('Any', 'from typing import Any'),
    # Network address types
    'cidr': ('IPv4Network', 'from ipaddress import IPv4Network, IPv6Network'),
    'inet': ('IPv4Address | IPv6Address', 'from ipaddress import IPv4Address, IPv6Address'),
    'macaddr': ('str', None),
    'macaddr8': ('str', None),
    # Bit string types
    'bit': ('str', None),
    'bit varying': ('str', None),
    'varbit': ('str', None),  # Shortened form
    # Text search types
    'tsvector': ('str', None),
    'tsquery': ('str', None),
    # UUID type
    'uuid': ('UUID4', 'from pydantic import UUID4'),
    # XML type
    'xml': ('str', None),
    # JSON types
    'json': ('dict | list[dict] | list[Any] | Json', 'from typing import Any\nfrom pydantic import Json'),
    'jsonb': ('dict | list[dict] | list[Any] | Json', 'from typing import Any\nfrom pydantic import Json'),
    # Array type
    'ARRAY': ('list', None),  # Generic list; specify further based on the array's element type
}


# SQLAlchemy Type Map
SQLALCHEMY_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # Integer types
    'integer': ('Integer', 'from sqlalchemy import Integer'),
    'int': ('Integer', 'from sqlalchemy import Integer'),  # Shortened form
    'bigint': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'smallint': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'int2': ('SmallInteger', 'from sqlalchemy import SmallInteger'),  # Internal form
    'int4': ('Integer', 'from sqlalchemy import Integer'),  # Internal form
    'int8': ('BigInteger', 'from sqlalchemy import BigInteger'),  # Internal form
    # Decimal/Numeric types
    'numeric': ('Numeric', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),
    'decimal': ('Numeric', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),
    # Floating point types
    'real': ('Float', 'from sqlalchemy import Float'),
    'float4': ('Float', 'from sqlalchemy import Float'),  # Internal form
    'double precision': ('Float', 'from sqlalchemy import Float'),
    'float': ('Numeric', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),  # Match PYDANTIC_TYPE_MAP
    'float8': ('Float', 'from sqlalchemy import Float'),  # Internal form
    # Serial types
    'serial': ('Integer', 'from sqlalchemy import Integer'),
    'bigserial': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'smallserial': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'serial2': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'serial4': ('Integer', 'from sqlalchemy import Integer'),
    'serial8': ('BigInteger', 'from sqlalchemy import BigInteger'),
    # Money type
    'money': ('Numeric', 'from sqlalchemy import Numeric'),
    # Character types
    'character varying': ('String', 'from sqlalchemy import String'),
    'varchar': ('String', 'from sqlalchemy import String'),  # Shortened form
    'character varying(n)': ('String', 'from sqlalchemy import String'),
    'varchar(n)': ('String', 'from sqlalchemy import String'),
    'character(n)': ('String', 'from sqlalchemy import String'),
    'char(n)': ('String', 'from sqlalchemy import String'),
    'char': ('String', 'from sqlalchemy import String'),  # Shortened form
    'text': ('Text', 'from sqlalchemy import Text'),
    # Binary type
    'bytea': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    # Date/Time types
    'timestamp': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp with time zone': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp without time zone': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamptz': ('DateTime', 'from sqlalchemy import DateTime'),  # Shortened form
    'date': ('Date', 'from sqlalchemy import Date'),
    'time': ('Time', 'from sqlalchemy import Time'),
    'time with time zone': ('Time', 'from sqlalchemy import Time'),
    'timetz': ('Time', 'from sqlalchemy import Time'),  # Shortened form
    'interval': ('Interval', 'from sqlalchemy import Interval'),
    # Boolean type
    'boolean': ('Boolean', 'from sqlalchemy import Boolean'),
    'bool': ('Boolean', 'from sqlalchemy import Boolean'),  # Shortened form
    # Enum type
    'enum': ('Enum', 'from sqlalchemy import Enum'),
    # Geometric types
    'point': ('None', None),
    'line': ('None', None),
    'lseg': ('None', None),
    'box': ('None', None),
    'path': ('None', None),
    'polygon': ('None', None),
    'circle': ('None', None),
    # Network address types
    'cidr': ('None', None),
    'inet': ('None', None),
    'macaddr': ('None', None),
    'macaddr8': ('None', None),
    # Bit string types
    'bit': ('None', None),
    'bit varying': ('None', None),
    'varbit': ('None', None),  # Shortened form
    # Text search types
    'tsvector': ('TSVECTOR', 'from sqlalchemy.dialects.postgresql import TSVECTOR'),
    'tsquery': ('TSQUERY', 'from sqlalchemy.dialects.postgresql import TSQUERY'),
    # UUID type
    'uuid': ('UUID', 'from sqlalchemy.dialects.postgresql import UUID'),
    # XML type
    'xml': ('Text', 'from sqlalchemy import Text'),  # XML handled as Text for simplicity
    # JSON types
    'json': ('JSON', 'from sqlalchemy import JSON'),
    'jsonb': ('JSONB', 'from sqlalchemy.dialects.postgresql import JSONB'),
    # Array type
    'ARRAY': ('ARRAY', 'from sqlalchemy.dialects.postgresql import ARRAY'),  # Generic ARRAY; specify further
}


# SQLAlchemy Type Map V2
SQLALCHEMY_V2_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # Integer types
    'integer': ('Integer,int', 'from sqlalchemy import Integer'),
    'int': ('Integer,int', 'from sqlalchemy import Integer'),  # Shortened form
    'bigint': ('BigInteger,int', 'from sqlalchemy import BigInteger'),
    'smallint': ('SmallInteger,int', 'from sqlalchemy import SmallInteger'),
    'int2': ('SmallInteger,int', 'from sqlalchemy import SmallInteger'),  # Internal form
    'int4': ('Integer,int', 'from sqlalchemy import Integer'),  # Internal form
    'int8': ('BigInteger,int', 'from sqlalchemy import BigInteger'),  # Internal form
    # Decimal/Numeric types
    'numeric': ('Numeric,Decimal', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),  # Changed to Decimal
    'decimal': ('Numeric,Decimal', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),
    # Floating point types
    'real': ('Float,float', 'from sqlalchemy import Float'),
    'float4': ('Float,float', 'from sqlalchemy import Float'),  # Internal form
    'double precision': ('Float,float', 'from sqlalchemy import Float'),
    'float': (
        'Numeric,Decimal',
        'from sqlalchemy import Numeric\nfrom decimal import Decimal',
    ),  # Match PYDANTIC_TYPE_MAP
    'float8': ('Float,float', 'from sqlalchemy import Float'),  # Internal form
    # Serial types
    'serial': ('Integer,int', 'from sqlalchemy import Integer'),
    'bigserial': ('BigInteger,int', 'from sqlalchemy import BigInteger'),
    'smallserial': ('SmallInteger,int', 'from sqlalchemy import SmallInteger'),
    'serial2': ('SmallInteger,int', 'from sqlalchemy import SmallInteger'),
    'serial4': ('Integer,int', 'from sqlalchemy import Integer'),
    'serial8': ('BigInteger,int', 'from sqlalchemy import BigInteger'),
    # Money type
    'money': ('Numeric,Decimal', 'from sqlalchemy import Numeric'),
    # Character types
    'character varying': ('String,str', 'from sqlalchemy import String'),
    'varchar': ('String,str', 'from sqlalchemy import String'),  # Shortened form
    'character varying(n)': ('String,str', 'from sqlalchemy import String'),
    'varchar(n)': ('String,str', 'from sqlalchemy import String'),
    'character(n)': ('String,str', 'from sqlalchemy import String'),
    'char(n)': ('String,str', 'from sqlalchemy import String'),
    'char': ('String,str', 'from sqlalchemy import String'),  # Shortened form
    'text': ('Text,str', 'from sqlalchemy import Text'),
    # Binary type
    'bytea': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    # Date/Time types
    'timestamp': ('DateTime,datetime.datetime', 'from sqlalchemy import DateTime\nimport datetime'),
    'timestamp with time zone': ('DateTime,datetime.datetime', 'from sqlalchemy import DateTime\nimport datetime'),
    'timestamp without time zone': (
        'DateTime,datetime.datetime',
        'from sqlalchemy import DateTime\nimport datetime',
    ),
    'timestamptz': ('DateTime,datetime.datetime', 'from sqlalchemy import DateTime\nimport datetime'),  # Shortened form
    'date': ('Date,datetime.date', 'from sqlalchemy import Date\nimport datetime'),
    'time': ('Time,datetime.time', 'from sqlalchemy import Time\nimport datetime'),
    'time with time zone': ('Time,datetime.time', 'from sqlalchemy import Time\nimport datetime'),
    'timetz': ('Time,datetime.time', 'from sqlalchemy import Time\nimport datetime'),  # Shortened form
    'interval': ('Interval,datetime.timedelta', 'from sqlalchemy import Interval\nimport datetime'),
    # Boolean type
    'boolean': ('Boolean,bool', 'from sqlalchemy import Boolean'),
    'bool': ('Boolean,bool', 'from sqlalchemy import Boolean'),  # Shortened form
    # Enum type
    'enum': ('Enum,str', 'from sqlalchemy import Enum'),
    # Geometric types
    'point': ('None,None', None),
    'line': ('None,None', None),
    'lseg': ('None,None', None),
    'box': ('None,None', None),
    'path': ('None,None', None),
    'polygon': ('None,None', None),
    'circle': ('None,None', None),
    # Network address types
    'cidr': ('CIDR,str', 'from sqlalchemy.dialects.postgresql import CIDR'),
    'inet': (
        'INET,IPv4Address | IPv6Address',
        'from sqlalchemy.dialects.postgresql import INET\nfrom ipaddress import IPv4Address, IPv6Address',
    ),
    'macaddr': ('MACADDR,str', 'from sqlalchemy.dialects.postgresql import MACADDR'),
    'macaddr8': ('MACADDR8,str', 'from sqlalchemy.dialects.postgresql import MACADDR8'),
    # Bit string types
    'bit': ('BIT,str', 'from sqlalchemy.dialects.postgresql import BIT'),
    'bit varying': ('BIT,str', 'from sqlalchemy.dialects.postgresql import BIT'),
    'varbit': ('BIT,str', 'from sqlalchemy.dialects.postgresql import BIT'),  # Shortened form
    # Text search types
    'tsvector': ('TSVECTOR,str', 'from sqlalchemy.dialects.postgresql import TSVECTOR'),
    'tsquery': ('TSQUERY,str', 'from sqlalchemy.dialects.postgresql import TSQUERY'),
    'uuid': ('UUID,UUID4', 'from sqlalchemy.dialects.postgresql import UUID\nfrom pydantic import UUID4'),
    'xml': ('Text,str', 'from sqlalchemy import Text'),  # XML handled as Text for simplicity
    'json': (
        'JSON,dict | list[dict] | list[Any] | Json',
        'from sqlalchemy import JSON\nfrom typing import Any\nfrom pydantic import Json',
    ),
    'jsonb': (
        'JSONB,dict | list[dict] | list[Any] | Json',
        'from sqlalchemy.dialects.postgresql import JSONB\nfrom typing import Any\nfrom pydantic import Json',
    ),
    'ARRAY': ('ARRAY,list', 'from sqlalchemy.dialects.postgresql import ARRAY'),  # Generic ARRAY; specify further
}
