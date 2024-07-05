import json
from dataclasses import asdict, dataclass, field
from random import random
import pprint

from faker import Faker

from supabase_pydantic.util.constants import (
    BASE_CLASS_POSTFIX,
    CONSTRAINT_TYPE_MAP,
    CUSTOM_MODEL_NAME,
    PYDANTIC_TYPE_MAP,
    SQLALCHEMY_TYPE_MAP,
    RelationType,
)
from supabase_pydantic.util.fake import generate_fake_data
from supabase_pydantic.util.string import to_pascal_case


pp = pprint.PrettyPrinter(indent=4)


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
    is_nullable: bool | None = True
    max_length: int | None = None
    primary: bool = False

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
        if 'time zone' in self.post_gres_datatype.lower():
            base_type = 'TIMESTAMP(timezone=True)'

        column_values = dict()
        column_values['nullable'] = 'True' if self.is_nullable else 'False'
        if self.primary:
            column_values['primary_key'] = 'True'

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

    def get_foreign_table_name(self, is_base: bool = False) -> str:
        """Get the foreign table name."""
        return (
            f'{to_pascal_case(self.foreign_table_name)}{BASE_CLASS_POSTFIX}'
            if is_base
            else to_pascal_case(self.foreign_table_name)
        )

    def get_jsonapi_relationship_info(self) -> dict[str, str]:
        """Get the JSONAPI relationship information for a foreign key."""
        rel_info = {'resource_type': f"'{self.foreign_table_name}'"}
        if self.relation_type == RelationType.MANY_TO_MANY or self.relation_type == RelationType.ONE_TO_MANY:
            rel_info['many'] = 'True'
        return rel_info

    def write_pydantic_column_string(self, is_base: bool = False) -> str:
        """Obtain the Pydantic field string for a foreign key."""
        # generate type
        foreign_table = self.get_foreign_table_name(is_base)
        data_type = f'list[{foreign_table}] | None'
        return f'{self.foreign_table_name}: {data_type} = None'

    def write_jsonapi_pydantic_column_string(self, is_base: bool = False) -> str:
        """Obtain the Pydantic field string for a foreign key."""
        # generate type
        foreign_table = (
            f'{to_pascal_case(self.foreign_table_name)}{BASE_CLASS_POSTFIX}'
            if is_base
            else to_pascal_case(self.foreign_table_name)
        )
        data_type = f'list[{foreign_table}] | None'

        relationship_info = self.get_jsonapi_relationship_info()
        relationship_info_string = 'RelationshipInfo('
        relationship_info_string += ','.join([f'\n\t\t\t{k}={v}' for k, v in relationship_info.items()])
        relationship_info_string += '\n\t\t)'

        fields = dict()
        fields['default'] = 'None'
        fields['relationship'] = relationship_info_string

        field_string = 'Field('
        field_string += ','.join([f'\n\t\t{k}={v}' for k, v in fields.items()])
        field_string += '\n\t)'

        return f'{self.foreign_table_name}: {data_type} = {field_string}'

    def write_jsonapi_sqlalchemy_column_string(self, is_base: bool = False) -> str:
        """Obtain the SQLAlchemy column string for a foreign key."""
        # generate type
        foreign_table = self.get_foreign_table_name(is_base)
        data_type = f'list[{foreign_table}]'

        return f'{self.foreign_table_name} = relationship("{foreign_table}")'

    def write_pydantic_forward_ref(self, is_base: bool = False) -> str:
        """Obtain the Pydantic forward reference string for a foreign key."""
        foreign_table = (
            f'{to_pascal_case(self.foreign_table_name)}{BASE_CLASS_POSTFIX}'
            if is_base
            else to_pascal_case(self.foreign_table_name)
        )
        return f"{foreign_table} = ForwardRef('{foreign_table}')"


@dataclass
class TableInfo(AsDictParent):
    name: str
    schema: str = 'public'
    columns: list[ColumnInfo] = field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)
    constraints: list[ConstraintInfo] = field(default_factory=list)
    generated_data: list[dict] = field(default_factory=list)

    def add_column(self, column: ColumnInfo):
        """Add a column to the table."""
        self.columns.append(column)

    def add_foreign_key(self, fk: ForeignKeyInfo):
        """Add a foreign key to the table."""
        self.foreign_keys.append(fk)

    def add_constraint(self, constraint: ConstraintInfo):
        """Add a constraint to the table."""
        self.constraints.append(constraint)

    def aliasing_in_columns(self) -> bool:
        """Check if any column within a table has an alias."""
        return any(bool(c.alias is not None) for c in self.columns)

    def table_dependencies(self) -> set[str]:
        """Get the table dependencies (foreign tables) for a table."""
        return set([fk.foreign_table_name for fk in self.foreign_keys])

    def table_forward_refs(self, is_base: bool = False) -> set[str]:
        """Get the table forward references for a table."""
        return set([fk.write_pydantic_forward_ref(is_base) for fk in self.foreign_keys])

    def primary_key(self) -> list[str]:
        """Get the primary key for a table."""
        return next(c.columns for c in self.constraints if c.constraint_type() == 'PRIMARY KEY')

    def primary_is_composite(self) -> bool:
        """Check if the primary key is composite."""
        return len(self.primary_key()) > 1

    def get_pydantic_imports(self) -> tuple[set[str], set[str]]:
        """Get the unique datatypes & import statements for a table."""
        dtypes, imports = set(), set()

        # standards
        imports.add('from pydantic import BaseModel')
        imports.add('from pydantic import Field')
        if len(self.table_dependencies()) > 0:
            # imports.add('from typing import ForwardRef')
            imports.add('from __future__ import annotations')

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

        if len(self.primary_key()) > 0:
            imports.add('from sqlalchemy import PrimaryKeyConstraint')

        for c in self.columns:
            dtype, import_str = c.get_sqlalchemy_import_information()
            if import_str is not None:
                imports.add(import_str)
            dtypes.add(dtype)

        return dtypes, imports

    def get_jsonapi_sqlalchemy_relationships(self, is_base: bool = False) -> list[dict]:
        """Get the JSONAPI relationship information for a table."""
        relationships = []
        for fk in self.foreign_keys:
            r = {}
            r['name'] = fk.foreign_table_name
            r['relationship_name'] = fk.get_foreign_table_name(is_base)
            r['back_populates'] = fk.foreign_table_name
        return relationships

    def _write_base_class_name(self) -> str:
        """Generate the name of the Pydantic parent class."""
        return f'{to_pascal_case(self.name)}{BASE_CLASS_POSTFIX}'

    def _write_pydantic_base_class_string(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str:
        """Generate the parent Pydantic model string for a table."""
        if isinstance(metaclass, list):
            metaclass = ', '.join(metaclass)
        return (
            f'class {self._write_base_class_name()}({metaclass}):'
            f'\n\t"""{to_pascal_case(self.name)} Base Schema."""\n'
        )

    def _get_columns_for_model(
        self, as_parent: bool = True
    ) -> tuple[list[ColumnInfo], list[ColumnInfo], list[str], list[str]]:
        """Sort and combine columns based on is_nullable attribute."""
        columns = self.sort_and_combine_columns_for_pydantic_model(as_parent)
        primary_columns = [c for c in columns if c.name in self.primary_key()]
        columns = [c for c in columns if c.name not in self.primary_key()]
        foreign_table_columns = [fk.write_pydantic_column_string(as_parent) for fk in self.foreign_keys]
        foreign_table_columns_jsonapi = [fk.write_jsonapi_pydantic_column_string(as_parent) for fk in self.foreign_keys]

        return primary_columns, columns, foreign_table_columns, foreign_table_columns_jsonapi

    def write_pydantic_base_class(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str:
        """Generate the Base Pydantic model for a table."""
        primary_columns, columns, foreign_table_columns, _ = self._get_columns_for_model()

        class_string = self._write_pydantic_base_class_string(metaclass) + '\n'
        if len(primary_columns) > 0:
            class_string += '\t# Primary Keys\n'
            class_string += '\n'.join([f'\t{c.write_pydantic_column_string()}' for c in primary_columns])
        if len(columns) > 0:
            if len(primary_columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Columns\n'
            class_string += '\n'.join([f'\t{c.write_pydantic_column_string()}' for c in columns])
        if len(foreign_table_columns) > 0:
            if len(primary_columns) > 0 or len(columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Foreign Keys\n' + '\n'.join([f'\t{c}' for c in foreign_table_columns])

        return class_string

    def write_pydantic_working_class(self) -> str:
        """Generate the Pydantic model string for a table based on the parent class."""
        to_join = [
            f'class {to_pascal_case(self.name)}({self._write_base_class_name()}):',
            f'\t"""{to_pascal_case(self.name)} Schema for Pydantic.',
            f'\n\tInherits from {self._write_base_class_name()}. Add any custom methods here.',
            '\t"""',
            '\tpass',
        ]
        return '\n'.join(to_join)

    def write_pydantic_forward_refs(self) -> str:
        """Generate the Pydantic forward reference string for a table."""
        return '\n'.join(self.table_forward_refs())

    def _write_sqlalchemy_parent_class(self) -> str:
        """Generate the parent SQLAlchemy model string for a table."""
        return f'class {to_pascal_case(self.name)}(Base):'

    def _write_sql_alchemy_table_args(self) -> list[str]:
        """Generate the SQLAlchemy table arguments for a table."""
        table_args = []
        for con in self.constraints:
            if con.constraint_type() == 'PRIMARY KEY':
                primary_cols = ', '.join([f"'{c}'" for c in con.columns])
                name_str = f"name='{con.constraint_name}'"
                table_args.append(f'PrimaryKeyConstraint({primary_cols}, {name_str}),')

        table_args.append("{ 'schema': 'public' }")
        return table_args

    def write_sqlalchemy_class(self) -> str:
        """Generate the SQLAlchemy model string for a table."""
        primary_columns, columns, _, _ = self._get_columns_for_model()
        table_args = self._write_sql_alchemy_table_args()

        class_string = self._write_sqlalchemy_parent_class() + f"\n\t__tablename__ = '{self.name}'\n"

        if len(primary_columns) > 0:
            class_string += '\n'
            class_string += '\t# Primary Keys\n'
            class_string += '\n'.join([f'\t{c.write_sqlalchemy_column_string()}' for c in primary_columns])
        if len(columns) > 0:
            class_string += '\n\n'
            class_string += '\t# Columns\n'
            class_string += '\n'.join([f'\t{c.write_sqlalchemy_column_string()}' for c in columns])
        if len(table_args) > 0:
            class_string += '\n\n'
            class_string += '\t# Table Args\n'
            class_string += '\t__table_args__ = (\n'
            class_string += '\n'.join([f'\t\t{arg}' for arg in table_args])
            class_string += '\n\t)\n'

        return class_string

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

    def get_fastapi_jsonapi_pydantic_imports(self) -> tuple[set[str], set[str]]:
        """Get the unique datatypes & import statements for a table."""
        dtypes, imports = set(), set()

        # standards
        imports.add('from pydantic import BaseModel as PydanticBaseModel')
        imports.add('from fastapi_jsonapi.schema_base import BaseModel, Field, RelationshipInfo')
        if len(self.table_dependencies()) > 0:
            imports.add('from __future__ import annotations')

        for c in self.columns:
            dtype, import_str = c.get_pydantic_import_information()
            if import_str is not None:
                imports.add(import_str)
            dtypes.add(dtype)

        return dtypes, imports

    def get_fastapi_jsonapi_sqlalchemy_imports(self) -> tuple[set[str], set[str]]:
        """Get the unique datatypes & import statements for a table."""
        dtypes, imports = set(), set()

        # standards
        imports.add('from sqlalchemy.ext.declarative import declarative_base')
        imports.add('from sqlalchemy import Column, ForeignKey')
        imports.add('from sqlalchemy.orm import relationship')

        if len(self.primary_key()) > 0:
            imports.add('from sqlalchemy import PrimaryKeyConstraint')

        for c in self.columns:
            dtype, import_str = c.get_sqlalchemy_import_information()
            if import_str is not None:
                imports.add(import_str)
            dtypes.add(dtype)

        return dtypes, imports

    def write_jsonapi_pydantic_base_class(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str:
        """Generate the Base Pydantic model for a table."""
        primary_columns, columns, _, foreign_table_columns = self._get_columns_for_model()

        class_string = self._write_pydantic_base_class_string(metaclass) + '\n'
        if len(primary_columns) > 0:
            class_string += '\t# Primary Keys\n'
            class_string += '\n'.join([f'\t{c.write_pydantic_column_string()}' for c in primary_columns])
        if len(columns) > 0:
            if len(primary_columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Columns\n'
            class_string += '\n'.join([f'\t{c.write_pydantic_column_string()}' for c in columns])
        if len(foreign_table_columns) > 0:
            if len(primary_columns) > 0 or len(columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Relationships\n' + '\n'.join([f'\t{c}' for c in foreign_table_columns])

        return class_string

    def write_jsonapi_pydantic_working_class(self) -> str:
        """Generate the Pydantic model string for a table based on the parent class."""
        b = self._write_base_class_name()
        working_class_types = ['Patch', 'Input', 'Item']

        working_class_string = ''
        for t in working_class_types:
            working_class_string += '\n\n' + '\n'.join(
                [
                    f'class {to_pascal_case(self.name)}{t}Schema({b}):',
                    f'\t"""{to_pascal_case(self.name)} {t} Schema."""',
                    '\tpass',
                ]
            )

        return working_class_string

    def write_jsonapi_sqlalchemy_class(self) -> str:
        pass

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
