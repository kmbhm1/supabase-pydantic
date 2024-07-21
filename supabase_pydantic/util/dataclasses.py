import json
import os
from dataclasses import asdict, dataclass, field
from enum import Enum
from random import random
from typing import Any, Literal, TypedDict

from faker import Faker

from supabase_pydantic.util.constants import CONSTRAINT_TYPE_MAP, RelationType
from supabase_pydantic.util.fake import generate_fake_data
from supabase_pydantic.util.util import get_pydantic_type, get_sqlalchemy_type


class AppConfig(TypedDict, total=False):
    default_directory: str
    overwrite_existing_files: bool
    nullify_base_schema: bool


class ToolConfig(TypedDict):
    supabase_pydantic: AppConfig


def get_enum_member_from_string(cls: Any, value: str) -> Any:
    """Get an Enum member from a string value."""
    value_lower = value.lower()
    for member in cls:
        if member.value == value_lower:
            return member
    raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class OrmType(Enum):
    """Enum for file types."""

    PYDANTIC = 'pydantic'
    SQLALCHEMY = 'sqlalchemy'


class FrameWorkType(Enum):
    """Enum for framework types."""

    FASTAPI = 'fastapi'
    FASTAPI_JSONAPI = 'fastapi-jsonapi'


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


@dataclass
class AsDictParent:
    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)


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
    name: str
    post_gres_datatype: str
    datatype: str
    alias: str | None = None
    default: str | None = None
    max_length: int | None = None
    is_nullable: bool | None = True
    primary: bool = False
    is_unique: bool = False
    is_foreign_key: bool = False

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


@dataclass
class ForeignKeyInfo(AsDictParent):
    constraint_name: str
    column_name: str
    foreign_table_name: str
    foreign_column_name: str
    foreign_table_schema: str = 'public'
    relation_type: RelationType | None = None  # E.g., "One-to-One", "One-to-Many"


@dataclass
class TableInfo(AsDictParent):
    name: str
    schema: str = 'public'
    table_type: Literal['BASE TABLE', 'VIEW'] = 'BASE TABLE'
    is_bridge: bool = False  # whether the table is a bridge table
    columns: list[ColumnInfo] = field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)
    constraints: list[ConstraintInfo] = field(default_factory=list)
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
        return (
            next(c.columns for c in self.constraints if c.constraint_type() == 'PRIMARY KEY')
            if self.table_type == 'BASE TABLE'
            else []
        )

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
    ) -> dict[str, list[ColumnInfo]]:
        """Sort and combine columns based on is_nullable attribute.

        Args:
            separate_nullable: Whether to separate nullable and non-nullable columns.
            separate_primary_key: Whether to separate primary key and secondary columns.

        Returns:
            A dictionary with keys, nullable, non_nullable, and remaining as keys
            and lists of ColumnInfo objects as values.
        """
        result: dict[str, list[ColumnInfo]] = {'keys': [], 'nullable': [], 'non_nullable': [], 'remaining': []}
        if separate_primary_key:
            result['keys'] = self.get_primary_columns(sort_results=True)
            result['remaining'] = self.get_secondary_columns(sort_results=True)
        else:
            result['remaining'] = sorted(self.columns, key=lambda x: x.name)

        if separate_nullable:
            nullable_columns = [column for column in result['remaining'] if column.is_nullable]  # already sorted
            non_nullable_columns = [column for column in result['remaining'] if not column.is_nullable]

            # Combine them with non-nullable first
            result['nullable'] = non_nullable_columns
            result['non_nullable'] = nullable_columns
            result['remaining'] = []

        return result

    def generate_fake_row(self) -> dict[str, Any]:
        """Generate a dictionary with column names as keys and fake data as values."""
        row: dict[str, Any] = {}
        fake = Faker()
        for column in self.columns:
            if column.is_nullable and random() < 0.1:
                row[column.name] = None
            else:
                is_nullable = column.is_nullable if column.is_nullable is not None else False
                row[column.name] = generate_fake_data(
                    column.post_gres_datatype, is_nullable, column.max_length, column.name, fake
                )
        return row
