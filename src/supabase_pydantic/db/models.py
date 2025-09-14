from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from supabase_pydantic.core.constants import OrmType
from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.drivers.postgres.constants import CONSTRAINT_TYPE_MAP
from supabase_pydantic.utils.serialization import AsDictParent
from supabase_pydantic.utils.types import get_pydantic_type, get_sqlalchemy_type


@dataclass
class UserDefinedType(AsDictParent):
    type_name: str
    namespace: str
    owner: str
    category: str
    is_defined: bool
    type: str
    input_function: str
    output_function: str
    receive_function: str
    send_function: str
    length: int
    by_value: bool
    alignment: str
    delimiter: str
    related_table: str
    element_type: str
    collation: str


@dataclass
class UserEnumType(AsDictParent):
    type_name: str
    namespace: str
    owner: str
    category: str
    is_defined: bool
    type: str
    enum_values: list[str] = field(default_factory=list)

    def matches_type_name(self, type_name: str) -> bool:
        """Check if a given type name matches this enum type, handling PostgreSQL array naming conventions."""
        if not type_name:
            return False

        # Remove all leading underscores (PostgreSQL array types add underscores)
        clean_name = type_name
        while clean_name.startswith('_'):
            clean_name = clean_name[1:]

        # Remove array brackets if present
        if clean_name.endswith('[]'):
            clean_name = clean_name[:-2]

        # Remove quotes if present
        if clean_name.startswith('"') and clean_name.endswith('"'):
            clean_name = clean_name[1:-1]

        # Handle schema qualification (e.g., public.Fifth_Type)
        if '.' in clean_name:
            clean_name = clean_name.split('.')[-1]

        # PostgreSQL sometimes lowercases type names for arrays
        # Compare both lowercased and original
        return self.type_name.lower() == clean_name.lower()


@dataclass
class UserTypeMapping(AsDictParent):
    column_name: str
    table_name: str
    namespace: str
    type_name: str
    type_category: str
    type_description: str


@dataclass
class ConstraintInfo(AsDictParent):
    constraint_name: str
    raw_constraint_type: str
    constraint_definition: str
    columns: list[str] = field(default_factory=list)

    def constraint_type(self) -> str:
        """Get the constraint type."""
        constraint_type: str = CONSTRAINT_TYPE_MAP.get(self.raw_constraint_type.lower(), 'OTHER')
        return constraint_type

    def __str__(self) -> str:
        """Return a string representation of the constraint."""
        return f'ConstraintInfo({self.constraint_name}, {self.constraint_type()})'


@dataclass
class ColumnInfo(AsDictParent):
    """Column information."""

    name: str
    post_gres_datatype: str
    datatype: str
    user_defined_values: list[str] | None = field(default_factory=list)
    unique_partners: list[str] | None = field(default_factory=list)
    alias: str | None = None
    default: str | None = None
    max_length: int | None = None
    is_nullable: bool | None = True
    primary: bool = False
    is_unique: bool = False
    is_foreign_key: bool = False
    constraint_definition: str | None = None
    is_identity: bool = False  # For auto-generated identity columns
    enum_info: EnumInfo | None = None  # New field for enum metadata
    array_element_type: str | None = None  # Stores element type for array columns
    description: str | None = None  # Stores the description of the column

    def __str__(self) -> str:
        """Return a string representation of the column."""
        return f'ColumnInfo({self.name}, {self.post_gres_datatype})'

    @property
    def has_default(self) -> bool:
        """Check if the column has a default value."""
        return self.default is not None

    @property
    def is_generated(self) -> bool:
        """Check if the column is auto-generated (identity or serial)."""
        return self.is_identity or (self.default is not None and 'nextval' in str(self.default).lower())

    def orm_imports(self, orm_type: OrmType = OrmType.PYDANTIC) -> set[str | None]:
        """Get the unique import statements for a column."""
        imports = set()  # future proofing in case multiple imports are needed
        if orm_type == OrmType.SQLALCHEMY:
            i = get_sqlalchemy_type(self.post_gres_datatype, ('Any', 'from sqlalchemy import Column'))[1]
        else:
            i = get_pydantic_type(self.post_gres_datatype)[1]
        imports.add(i)
        return imports

    def orm_datatype(self, orm_type: OrmType = OrmType.PYDANTIC) -> str:
        """Get the datatype for a column."""
        if orm_type == OrmType.SQLALCHEMY:
            sql_datatype: str = get_sqlalchemy_type(self.post_gres_datatype)[0]
            return sql_datatype

        pydantic_datatype: str = get_pydantic_type(self.post_gres_datatype)[0]
        return pydantic_datatype

    def is_user_defined_type(self) -> bool:
        """Check if the column is a user-defined type."""
        return self.post_gres_datatype == 'USER-DEFINED'

    def nullable(self) -> bool:
        """Check if the column is nullable."""
        return self.is_nullable if self.is_nullable is not None else False


@dataclass
class ForeignKeyInfo(AsDictParent):
    constraint_name: str
    column_name: str
    foreign_table_name: str
    foreign_column_name: str
    foreign_table_schema: str = 'public'
    relation_type: RelationType | None = None  # E.g., "One-to-One", "One-to-Many"


@dataclass
class SortedColumns:
    primary_keys: list[ColumnInfo]
    nullable: list[ColumnInfo]
    non_nullable: list[ColumnInfo]
    remaining: list[ColumnInfo]


@dataclass
class RelationshipInfo(AsDictParent):
    table_name: str
    related_table_name: str
    relation_type: RelationType | None = None  # E.g., "One-to-One", "One-to-Many"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RelationshipInfo):
            return NotImplemented
        return (
            self.table_name == other.table_name
            and self.related_table_name == other.related_table_name
            and self.relation_type == other.relation_type
        )


@dataclass
class TableInfo(AsDictParent):
    name: str
    schema: str = 'public'
    table_type: Literal['BASE TABLE', 'VIEW'] = 'BASE TABLE'
    is_bridge: bool = False  # whether the table is a bridge table
    columns: list[ColumnInfo] = field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)
    constraints: list[ConstraintInfo] = field(default_factory=list)
    relationships: list[RelationshipInfo] = field(default_factory=list)
    generated_data: list[dict] = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the table."""
        return f'TableInfo({self.schema}.{self.name})'

    def add_column(self, column: ColumnInfo) -> None:
        """Add a column to the table."""
        self.columns.append(column)

    def add_foreign_key(self, fk: ForeignKeyInfo) -> None:
        """Add a foreign key to the table."""
        self.foreign_keys.append(fk)

    def add_constraint(self, constraint: ConstraintInfo) -> None:
        """Add a constraint to the table."""
        self.constraints.append(constraint)

    def aliasing_in_columns(self) -> bool:
        """Check if any column within a table has an alias."""
        return any(bool(c.alias is not None) for c in self.columns)

    def table_dependencies(self) -> set[str]:
        """Get the table dependencies (foreign tables) for a table."""
        return set([fk.foreign_table_name for fk in self.foreign_keys])

    def primary_key(self) -> list[str]:
        """Get the primary key for a table."""
        if self.table_type == 'BASE TABLE':
            for constraint in self.constraints:
                if constraint.constraint_type() == 'PRIMARY KEY':
                    return constraint.columns
        return []  # Return an empty list if no primary key is found

    def primary_is_composite(self) -> bool:
        """Check if the primary key is composite."""
        return len(self.primary_key()) > 1

    def get_primary_columns(self, sort_results: bool = False) -> list[ColumnInfo]:
        """Get the primary columns for a table."""
        return self._get_columns(is_primary=True, sort_results=sort_results)

    def get_secondary_columns(self, sort_results: bool = False) -> list[ColumnInfo]:
        """Get the secondary columns for a table."""
        return self._get_columns(is_primary=False, sort_results=sort_results)

    def _get_columns(self, is_primary: bool = True, sort_results: bool = False) -> list[ColumnInfo]:
        """Private function to get the primary or secondary columns for a table."""
        if is_primary:
            res = [c for c in self.columns if c.name in self.primary_key()]
        else:
            res = [c for c in self.columns if c.name not in self.primary_key()]

        if sort_results:
            res.sort(key=lambda x: x.name)

        return res

    def sort_and_separate_columns(
        self, separate_nullable: bool = False, separate_primary_key: bool = False
    ) -> SortedColumns:
        """Sort and combine columns based on is_nullable attribute.

        Args:
            separate_nullable: Whether to separate nullable and non-nullable columns.
            separate_primary_key: Whether to separate primary key and secondary columns.

        Returns:
            A dictionary with keys, nullable, non_nullable, and remaining as keys
            and lists of ColumnInfo objects as values.
        """
        # result: dict[str, list[ColumnInfo]] = {'keys': [], 'nullable': [], 'non_nullable': [], 'remaining': []}
        result: SortedColumns = SortedColumns([], [], [], [])
        if separate_primary_key:
            result.primary_keys = self.get_primary_columns(sort_results=True)
            result.remaining = self.get_secondary_columns(sort_results=True)
        else:
            result.remaining = sorted(self.columns, key=lambda x: x.name)

        if separate_nullable:
            nullable_columns = [column for column in result.remaining if column.is_nullable]  # already sorted
            non_nullable_columns = [column for column in result.remaining if not column.is_nullable]

            # Combine them with non-nullable first
            result.nullable = nullable_columns
            result.non_nullable = non_nullable_columns
            result.remaining = []

        return result

    def has_unique_constraint(self) -> bool:
        """Check if the table has unique constraints."""
        return any(c.constraint_type() == 'UNIQUE' for c in self.constraints)


# Connection Models


class DatabaseConnectionParams(BaseModel):
    """Base model for database connection parameters."""

    conn_type: str = Field(..., description="Connection type identifier (e.g., 'postgresql', 'mysql')")


class DirectConnectionParams(DatabaseConnectionParams):
    """Connection parameters for direct database connection."""

    dbname: str = Field(..., description='Database name')
    user: str = Field(..., description='Username for database connection')
    password: str = Field(..., description='Password for database connection')
    host: str = Field(..., description='Database host')
    port: str = Field(..., description='Database port')


class URLConnectionParams(DatabaseConnectionParams):
    """Connection parameters for URL-based database connection."""

    db_url: str = Field(
        ..., description='Database connection URL in format: dialect://username:password@host:port/database'
    )


class PostgresConnectionParams(BaseModel):
    """Connection parameters for PostgreSQL database."""

    # Either db_url or direct connection params must be provided
    dbname: str | None = Field(None, description='Database name')
    user: str | None = Field(None, description='Username for database connection')
    password: str | None = Field(None, description='Password for database connection')
    host: str | None = Field(None, description='Database host')
    port: str | None = Field(None, description='Database port')
    db_url: str | None = Field(
        None, description='Database connection URL in format: postgresql://username:password@host:port/database'
    )

    @field_validator('db_url')
    def validate_db_url(cls, v: str | None) -> str | None:
        """Validate db_url format."""
        if v is not None:
            # Basic validation that it starts with postgresql://
            if not v.startswith('postgresql://'):
                raise ValueError("PostgreSQL connection URL must start with 'postgresql://'")
        return v

    @field_validator('port')
    def validate_port(cls, v: str | int | None) -> str | None:
        """Validate port is numeric."""
        if v is not None:
            # Convert to int if it's a string
            if isinstance(v, str):
                try:
                    return str(int(v))
                except ValueError:
                    raise ValueError('Port must be a valid number')
            # Convert int to str to ensure consistent return type
            elif isinstance(v, int):
                return str(v)
        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        # Handle both Pydantic v1 and v2 APIs
        if hasattr(self, 'model_dump'):
            # Pydantic v2
            return {k: v for k, v in self.model_dump().items() if v is not None}
        else:
            # Pydantic v1
            return {k: v for k, v in self.dict().items() if v is not None}

    def is_valid(self) -> bool:
        """Check if parameters are valid for connection."""
        if self.db_url is not None:
            return True
        required_direct_params = [self.dbname, self.user, self.password, self.host, self.port]
        return all(param is not None for param in required_direct_params)

    model_config = ConfigDict(extra='forbid')


class MySQLConnectionParams(BaseModel):
    """MySQL connection parameters."""

    db_url: str | None = None
    dbname: str | None = None
    user: str | None = None
    password: str | None = None
    host: str | None = None
    port: str | None = Field(default='3306', description='MySQL default port is 3306')

    @field_validator('port')
    def validate_port(cls, v: str | int | None) -> str | None:
        """Validate that port is a valid integer."""
        if v is not None:
            if isinstance(v, str):
                try:
                    return str(int(v))
                except ValueError:
                    raise ValueError('Port must be a valid number')
            # Convert int to str to ensure consistent return type
            elif isinstance(v, int):
                return str(v)
        return v

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        # Handle both Pydantic v1 and v2 APIs
        if hasattr(self, 'model_dump'):
            # Pydantic v2
            return {k: v for k, v in self.model_dump().items() if v is not None}
        else:
            # Pydantic v1
            return {k: v for k, v in self.dict().items() if v is not None}

    def is_valid(self) -> bool:
        """Check if parameters are valid for connection."""
        if self.db_url is not None:
            return True
        return all([self.dbname, self.user, self.password, self.host, self.port])

    model_config = ConfigDict(extra='forbid')
