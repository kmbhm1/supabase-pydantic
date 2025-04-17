import json
from dataclasses import asdict, dataclass, field
from typing import Literal

from supabase_pydantic.util.constants import CONSTRAINT_TYPE_MAP, OrmType, RelationType
from supabase_pydantic.util.util import get_pydantic_type, get_sqlalchemy_type


@dataclass
class EnumInfo:
    name: str  # The name of the enum type in the DB
    values: list[str]  # The possible values for the enum
    schema: str = 'public'  # The schema, defaulting to 'public'

    def python_class_name(self) -> str:
        """Converts DB enum name to PascalCase for Python class, prefixed by schema.

        e.g., 'order_status' in 'public' -> 'PublicOrderStatusEnum'
        """
        class_name = ''.join(word.capitalize() for word in self.name.split('_')) + 'Enum'
        return f'{self.schema.capitalize()}{class_name}'

    def python_member_name(self, value: str) -> str:
        """Converts enum value to a valid Python identifier.

        e.g., 'pending_new' -> 'pending_new'
        """
        return value.lower()


@dataclass
class AsDictParent:
    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)


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
        return CONSTRAINT_TYPE_MAP.get(self.raw_constraint_type.lower(), 'OTHER')


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
            return get_sqlalchemy_type(self.post_gres_datatype)[0]

        return get_pydantic_type(self.post_gres_datatype)[0]

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
