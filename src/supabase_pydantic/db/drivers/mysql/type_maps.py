"""MySQL type mappings to Python types."""

MYSQL_PYDANTIC_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # Numeric types
    'tinyint': ('bool', None),  # tinyint(1) is commonly used as boolean in MySQL
    'smallint': ('int', None),
    'mediumint': ('int', None),
    'int': ('int', None),
    'bigint': ('int', None),
    'decimal': ('Decimal', 'from decimal import Decimal'),
    'numeric': ('Decimal', 'from decimal import Decimal'),  # Added numeric type
    'float': ('float', None),
    'double': ('float', None),
    'bit': ('bool', None),  # MySQL bit type typically used for booleans
    # String types
    'char': ('str', None),
    'varchar': ('str', None),
    'tinytext': ('str', None),
    'text': ('str', None),
    'mediumtext': ('str', None),
    'longtext': ('str', None),
    # Date/Time types
    'date': ('datetime.date', 'import datetime'),
    'datetime': ('datetime.datetime', 'import datetime'),
    'timestamp': ('datetime.datetime', 'import datetime'),
    'time': ('datetime.time', 'import datetime'),
    'year': ('int', None),
    # Binary types
    'binary': ('bytes', None),
    'varbinary': ('bytes', None),
    'tinyblob': ('bytes', None),
    'blob': ('bytes', None),
    'mediumblob': ('bytes', None),
    'longblob': ('bytes', None),
    # Other types
    'enum': ('str', None),  # MySQL native enum
    'set': ('set[str]', 'from typing import Set'),
    'json': ('dict | list[dict] | list[Any] | Json', 'from typing import Any\nfrom pydantic import Json'),
    'jsonb': ('dict | list[dict] | list[Any] | Json', 'from typing import Any\nfrom pydantic import Json'),
    'boolean': ('bool', None),
    'bool': ('bool', None),
}

# SQLAlchemy Type Map for MySQL
MYSQL_SQLALCHEMY_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # Numeric types
    'tinyint': ('Boolean', 'from sqlalchemy import Boolean'),  # Map to Boolean for tinyint
    'smallint': ('SmallInteger', 'from sqlalchemy import SmallInteger'),
    'mediumint': ('Integer', 'from sqlalchemy import Integer'),
    'int': ('Integer', 'from sqlalchemy import Integer'),
    'bigint': ('BigInteger', 'from sqlalchemy import BigInteger'),
    'decimal': ('Numeric,Decimal', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),
    'float': ('Numeric,Decimal', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),
    'double': ('Float', 'from sqlalchemy import Float'),
    'bit': ('Boolean', 'from sqlalchemy import Boolean'),  # Map bit to Boolean for SQLAlchemy
    # String types
    'char': ('String', 'from sqlalchemy import String'),
    'varchar': ('String', 'from sqlalchemy import String'),
    'tinytext': ('Text', 'from sqlalchemy import Text'),
    'text': ('Text', 'from sqlalchemy import Text'),
    'mediumtext': ('Text', 'from sqlalchemy import Text'),
    'longtext': ('Text', 'from sqlalchemy import Text'),
    # Date/Time types
    'date': ('Date', 'from sqlalchemy import Date'),
    'datetime': ('DateTime', 'from sqlalchemy import DateTime'),
    'timestamp': ('DateTime', 'from sqlalchemy import DateTime'),
    'time': ('Time', 'from sqlalchemy import Time'),
    'year': ('Integer', 'from sqlalchemy import Integer'),
    # Binary types
    'binary': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'varbinary': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'tinyblob': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'blob': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'mediumblob': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    'longblob': ('LargeBinary', 'from sqlalchemy import LargeBinary'),
    # Other types
    'enum': ('Enum', 'from sqlalchemy import Enum'),
    'set': ('String', 'from sqlalchemy import String'),  # No direct SET equivalent
    'json': ('JSON', 'from sqlalchemy import JSON'),
    'boolean': ('Boolean', 'from sqlalchemy import Boolean'),
    'bool': ('Boolean', 'from sqlalchemy import Boolean'),
}

# SQLAlchemy V2 Type Map for MySQL
MYSQL_SQLALCHEMY_V2_TYPE_MAP: dict[str, tuple[str, str | None]] = {
    # Numeric types
    'tinyint': ('Boolean,bool', 'from sqlalchemy import Boolean'),  # Map to Boolean for tinyint
    'smallint': ('SmallInteger,int', 'from sqlalchemy import SmallInteger'),
    'mediumint': ('Integer,int', 'from sqlalchemy import Integer'),
    'int': ('Integer,int', 'from sqlalchemy import Integer'),
    'bigint': ('BigInteger,int', 'from sqlalchemy import BigInteger'),
    'decimal': ('Numeric,Decimal', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),
    'numeric': ('Numeric,Decimal', 'from sqlalchemy import Numeric\nfrom decimal import Decimal'),  # Added numeric type
    'float': ('Float,float', 'from sqlalchemy import Float'),
    'double': ('Float,float', 'from sqlalchemy import Float'),
    'bit': ('Boolean,bool', 'from sqlalchemy import Boolean'),  # Map bit to Boolean for SQLAlchemy v2
    # String types
    'char': ('String,str', 'from sqlalchemy import String'),
    'varchar': ('String,str', 'from sqlalchemy import String'),
    'tinytext': ('Text,str', 'from sqlalchemy import Text'),
    'text': ('Text,str', 'from sqlalchemy import Text'),
    'mediumtext': ('Text,str', 'from sqlalchemy import Text'),
    'longtext': ('Text,str', 'from sqlalchemy import Text'),
    # Date/Time types
    'date': ('Date,datetime.date', 'from sqlalchemy import Date\nimport datetime'),
    'datetime': ('DateTime,datetime.datetime', 'from sqlalchemy import DateTime\nimport datetime'),
    'timestamp': ('DateTime,datetime.datetime', 'from sqlalchemy import DateTime\nimport datetime'),
    'time': ('Time,datetime.time', 'from sqlalchemy import Time\nimport datetime'),
    'year': ('Integer,int', 'from sqlalchemy import Integer'),
    # Binary types
    'binary': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    'varbinary': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    'tinyblob': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    'blob': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    'mediumblob': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    'longblob': ('LargeBinary,bytes', 'from sqlalchemy import LargeBinary'),
    # Other types
    'enum': ('Enum,str', 'from sqlalchemy import Enum'),
    'set': ('String,set[str]', 'from sqlalchemy import String\nfrom typing import Set'),
    'json': (
        'JSON,dict | list[dict] | list[Any] | Json',
        'from sqlalchemy import JSON\nfrom typing import Any\nfrom pydantic import Json',
    ),
    'jsonb': (
        'JSONB,dict | list[dict] | list[Any] | Json',
        'from sqlalchemy.dialects.postgresql import JSONB\nfrom typing import Any\nfrom pydantic import Json',
    ),
    'boolean': ('Boolean,bool', 'from sqlalchemy import Boolean'),
    'bool': ('Boolean,bool', 'from sqlalchemy import Boolean'),
}
