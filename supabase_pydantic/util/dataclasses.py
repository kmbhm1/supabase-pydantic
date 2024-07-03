import json
from dataclasses import asdict, dataclass, field
from random import random

from faker import Faker

from supabase_pydantic.util.constants import CUSTOM_MODEL_NAME, PYDANTIC_TYPE_MAP, SQLALCHEMY_TYPE_MAP, RelationType
from supabase_pydantic.util.fake import generate_fake_data
from supabase_pydantic.util.string import to_pascal_case


@dataclass
class AsDictParent:
    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)


@dataclass
class ColumnInfo(AsDictParent):
    name: str
    post_gres_datatype: str
    datatype: str
    alias: str | None = None
    default: str | None = None
    is_nullable: bool | None = True
    max_length: int | None = None

    def write_pydantic_column_string(self) -> str:
        """Obtain the Pydantic field string for a column."""
        # generate type
        base_type = PYDANTIC_TYPE_MAP.get(self.post_gres_datatype, ('str', None))[0]
        data_type = f'{base_type} | None' if self.is_nullable else base_type

        field_values = dict()
        if self.is_nullable is not None and self.is_nullable:
            field_values['default'] = 'None'
        if self.alias is not None:
            field_values['alias'] = f'"{self.alias}"'

        # generate final string
        column_string = f'{self.name}: {data_type}'
        if len(field_values) > 0:
            field_values_str = ', '.join([f'{k}={v}' for k, v in field_values.items()])
            column_string += f' = Field({field_values_str})'

        return column_string

    def get_pydantic_import_information(self) -> tuple[str, str | None]:
        """Obtain the data type and import string for a column."""
        default = ('Any', 'from typing import Any')
        return PYDANTIC_TYPE_MAP.get(self.post_gres_datatype, default)

    def write_sqlalchemy_column_string(self) -> str:
        """Obtain the SQLAlchemy column string for a column."""
        # generate type
        base_type = SQLALCHEMY_TYPE_MAP.get(self.post_gres_datatype, ('String', None))[0]
        if base_type.lower() == 'uuid':
            base_type = 'UUID(as_uuid=True)'

        column_values = dict()
        column_values['nullable'] = 'True' if self.is_nullable else 'False'

        column_values_string = ', '.join([f'{k}={v}' for k, v in column_values.items()])

        # generate final string
        return f'{self.name} = Column({base_type}{", " + column_values_string if column_values_string else ""})'

    def get_sqlalchemy_import_information(self) -> tuple[str, str | None]:
        """Obtain the data type and import string for a column."""
        default = ('Any', 'from sqlalchemy import Column')
        return SQLALCHEMY_TYPE_MAP.get(self.post_gres_datatype, default)


@dataclass
class ForeignKeyInfo(AsDictParent):
    constraint_name: str
    column_name: str
    foreign_table_name: str
    foreign_column_name: str
    relation_type: RelationType  # E.g., "One-to-One", "One-to-Many"
    foreign_table_schema: str = 'public'

    def write_pydantic_column_string(self, is_base: bool = False) -> str:
        """Obtain the Pydantic field string for a foreign key."""
        # generate type
        foreign_table = (
            f'{to_pascal_case(self.foreign_table_name)}BaseSchema'
            if is_base
            else to_pascal_case(self.foreign_table_name)
        )
        data_type = f'list[{foreign_table}] | None'
        return f'{self.foreign_table_name}: {data_type} = None'

    def write_pydantic_forward_ref(self, is_base: bool = False) -> str:
        """Obtain the Pydantic forward reference string for a foreign key."""
        foreign_table = (
            f'{to_pascal_case(self.foreign_table_name)}BaseSchema'
            if is_base
            else to_pascal_case(self.foreign_table_name)
        )
        return f"{foreign_table} = ForwardRef('{foreign_table}')"


@dataclass
class TableInfo(AsDictParent):
    name: str
    schema: str = 'public'
    columns: list[ColumnInfo] = field(default_factory=list)
    generated_data: list[dict] = field(default_factory=list)  # Stores rows of generated data
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)

    def add_column(self, column: ColumnInfo):
        """Add a column to the table."""
        self.columns.append(column)

    def add_foreign_key(self, fk: ForeignKeyInfo):
        """Add a foreign key to the table."""
        self.foreign_keys.append(fk)

    def aliasing_in_columns(self) -> bool:
        """Check if any column within a table has an alias."""
        return any(bool(c.alias is not None) for c in self.columns)

    def table_dependencies(self) -> set[str]:
        """Get the table dependencies (foreign tables) for a table."""
        return set([fk.foreign_table_name for fk in self.foreign_keys])

    def table_forward_refs(self, is_base: bool = False) -> set[str]:
        """Get the table forward references for a table."""
        return set([fk.write_pydantic_forward_ref(is_base) for fk in self.foreign_keys])

    def get_pydantic_imports(self) -> tuple[set[str], set[str]]:
        """Get the unique datatypes & import statements for a table."""
        dtypes, imports = set(), set()

        # standards
        imports.add('from pydantic import BaseModel')
        if len(self.table_dependencies()) > 0:
            # imports.add('from typing import ForwardRef')
            imports.add('from __future__ import annotations')
        if self.aliasing_in_columns():
            imports.add('from pydantic import Field')

        for c in self.columns:
            dtype, import_str = c.get_pydantic_import_information()
            if import_str is not None:
                imports.add(import_str)
            dtypes.add(dtype)

        return dtypes, imports

    def get_sqlalchemy_imports(self) -> tuple[set[str], set[str]]:
        """Get the unique datatypes & import statements for a table."""
        dtypes, imports = set(), set()

        # standards
        imports.add('from sqlalchemy.ext.declarative import declarative_base')
        imports.add('from sqlalchemy import Column')

        for c in self.columns:
            dtype, import_str = c.get_sqlalchemy_import_information()
            if import_str is not None:
                imports.add(import_str)
            dtypes.add(dtype)

        return dtypes, imports

    def _write_base_class_name(self) -> str:
        """Generate the name of the Pydantic parent class."""
        return f'{to_pascal_case(self.name)}BaseSchema'

    def _write_pydantic_base_class_string(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str:
        """Generate the parent Pydantic model string for a table."""
        if isinstance(metaclass, list):
            metaclass = ', '.join(metaclass)
        return (
            f'class {self._write_base_class_name()}({metaclass}):'
            f'\n\t"""{to_pascal_case(self.name)} Base Schema."""\n'
        )

    def write_pydantic_base_class(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str:
        """Generate the parent Pydantic model for a table."""
        columns = self.sort_and_combine_columns_for_pydantic_model(True)
        foreign_table_columns = [fk.write_pydantic_column_string(True) for fk in self.foreign_keys]

        to_join = [self._write_pydantic_base_class_string(metaclass)] + [
            f'\t{c.write_pydantic_column_string()}' for c in columns
        ]
        if len(foreign_table_columns) > 0:
            to_join += ['\n\t# Foreign Keys:'] + [f'\t{c}' for c in foreign_table_columns]

        return '\n'.join(to_join)

    def write_pydantic_working_class(self) -> str:
        """Generate the Pydantic model string for a table based on the parent class."""
        # foreign_table_columns = [fk.write_pydantic_column_string() for fk in self.foreign_keys]
        # to_join = [f'class {to_pascal_case(self.name)}({self._write_base_class_name()}):']
        # if len(foreign_table_columns) > 0:
        #     to_join += [f'\t{c}' for c in foreign_table_columns]
        # else:
        #     to_join.append('\tpass')

        to_join = [f'class {to_pascal_case(self.name)}({self._write_base_class_name()}):', '\tpass']
        return '\n'.join(to_join)

    def write_pydantic_forward_refs(self) -> str:
        """Generate the Pydantic forward reference string for a table."""
        return '\n'.join(self.table_forward_refs())

    def _write_sqlalchemy_parent_class(self) -> str:
        """Generate the parent SQLAlchemy model string for a table."""
        return f'class {to_pascal_case(self.name)}(Base):'

    def write_sqlalchemy_class(self) -> str:
        """Generate the SQLAlchemy model string for a table."""
        columns = self.sort_and_combine_columns_for_pydantic_model(False)
        return '\n'.join(
            [self._write_sqlalchemy_parent_class(), f"\t__tablename__ = '{self.name}'\n"]
            + [f'\t{c.write_sqlalchemy_column_string()}' for c in columns]
        )

    def sort_and_combine_columns_for_pydantic_model(self, return_parent_models: bool = True):
        """Sort and combine columns based on is_nullable attribute."""
        result_columns = self.columns

        if return_parent_models:
            result_columns.sort(key=lambda x: x.name)
        else:
            # Split the columns based on is_nullable attribute
            nullable_columns = [column for column in self.columns if column.is_nullable]
            non_nullable_columns = [column for column in self.columns if not column.is_nullable]

            # Sort each list alphabetically by column name
            nullable_columns.sort(key=lambda x: x.name)
            non_nullable_columns.sort(key=lambda x: x.name)

            # Combine them with non-nullable first
            result_columns = non_nullable_columns + nullable_columns

        return result_columns

    def generate_fake_row(self):
        """Generate a dictionary with column names as keys and fake data as values."""
        row = {}
        fake = Faker()
        for column in self.columns:
            if column.is_nullable and random.random() < 0.1:
                row[column.name] = None
            else:
                row[column.name] = generate_fake_data(
                    column.post_gres_datatype, column.is_nullable, column.max_length, column.name, fake
                )
        return row
