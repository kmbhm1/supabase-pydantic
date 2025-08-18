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


# SQLAlchemy Type Map
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


# SQLAlchemy Type Map V2
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
