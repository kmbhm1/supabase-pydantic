from typing import Any

from supabase_pydantic.core.constants import WriterClassType
from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.core.writers.abstract import AbstractClassWriter, AbstractFileWriter, get_section_comment
from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import ColumnInfo, SortedColumns, TableInfo
from supabase_pydantic.utils.types import get_sqlalchemy_v2_type


def pluralize(word: str) -> str:
    """Simple English pluralization function.

    Adds 's' to the end of a word, with special cases for common patterns.
    """
    # Common irregular plurals
    if word.endswith('y') and len(word) > 1 and word[-2] not in 'aeiou':
        return word[:-1] + 'ies'
    elif word.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    # Default case - just add 's'
    return word + 's'


# FastAPI


class SqlAlchemyFastAPIClassWriter(AbstractClassWriter):
    def __init__(
        self,
        table: TableInfo,
        class_type: WriterClassType = WriterClassType.BASE,
        null_defaults: bool = False,
        singular_names: bool = False,
        database_type: DatabaseType = DatabaseType.POSTGRES,
    ):
        super().__init__(table, class_type, null_defaults, singular_names, database_type)
        self._tname = self._generate_class_name(self.table.name)
        # Access schema from the table object
        self.schema = self.table.schema
        self.separated_columns: SortedColumns = self.table.sort_and_separate_columns(
            separate_nullable=True, separate_primary_key=True
        )

    def write_name(self) -> str:
        """Method to generate the header for the base class."""
        base_name = self._tname
        result: str = base_name

        # Add appropriate suffix for different model types
        if self.class_type == WriterClassType.INSERT:
            result = f'{base_name}Insert'
        elif self.class_type == WriterClassType.UPDATE:
            result = f'{base_name}Update'
        elif self.class_type == WriterClassType.BASE:
            result = base_name
        else:
            result = base_name

        return result

    def write_metaclass(self, metaclasses: list[str] | None = None) -> str | None:
        """Method to generate the metaclasses for the class."""
        return 'Base'

    def write_docs(self) -> str:
        """Method to generate class documentation."""
        # Base class
        tablename_str = ''

        if self.class_type in [WriterClassType.BASE, WriterClassType.BASE_WITH_PARENT]:
            qualifier = 'base class'
            if self.schema != 'public':
                tablename_str = f'{self.schema}.{self.table.name}'
            else:
                tablename_str = f'{self.table.name}'

        # Derived classes that support CRUD operations
        elif self.class_type == WriterClassType.INSERT:
            qualifier = 'Insert model'
            tablename_str = f'\n\n\t# Use this model for inserting new records into {self.table.name} table.\n'
            tablename_str += '\t# Auto-generated and identity fields are excluded.\n'
            tablename_str += '\t# Fields with defaults are optional.\n'
            primary_keys = [c.name for c in self.table.columns if c.primary]
            if primary_keys:
                tablename_str += f'\t# Primary key field(s): {", ".join(primary_keys)}\n'
            required_fields = [
                c.name
                for c in self.table.columns
                if not (c.is_nullable or c.has_default or c.is_identity or c.is_generated)
            ]
            if required_fields:
                tablename_str += f'\t# Required fields: {", ".join(required_fields)}'
        elif self.class_type == WriterClassType.UPDATE:
            qualifier = 'Update model'
            tablename_str = f'\n\n\t# Use this model for updating existing records in {self.table.name} table.\n'
            tablename_str += '\t# All fields are optional to support partial updates.\n'
            primary_keys = [c.name for c in self.table.columns if c.primary]
            if primary_keys:
                pk_str = ', '.join(primary_keys)
                tablename_str += f'\t# Primary key field(s) should be used to identify records: {pk_str}'
        else:
            qualifier = 'model'

        if self.class_type in [WriterClassType.BASE, WriterClassType.BASE_WITH_PARENT]:
            table_comment = '' if not tablename_str else '\n\n\t# Class for table: ' + tablename_str
            return f'\n\t"""{self._tname} {qualifier}."""{table_comment}'
        else:
            return f'\n\t"""{self._tname} {qualifier}."""{tablename_str}'

    def write_column(self, c: ColumnInfo) -> str:
        """Method to generate column definition for the class."""
        # Skip auto-generated fields for Insert and Update models
        if (self.class_type in [WriterClassType.INSERT, WriterClassType.UPDATE]) and c.is_identity:
            return ''

        # base type
        base_type, pyth_type, import_type = get_sqlalchemy_v2_type(
            c.post_gres_datatype, database_type=self.database_type
        )
        # Handle special types
        if base_type.lower() == 'uuid':
            base_type = 'UUID(as_uuid=True)'
        elif 'with time zone' in c.post_gres_datatype.lower():
            base_type = 'TIMESTAMP(timezone=True)'
        # Handle enum types
        elif c.enum_info is not None:
            # Use PostgreSQL enum type
            enum_class_name = c.enum_info.python_class_name()
            base_type = (
                f'Enum(*{enum_class_name}._member_names_, name="{c.enum_info.name}", schema="{c.enum_info.schema}")'
            )

        # For Update models, all fields are optional
        force_optional = self.class_type == WriterClassType.UPDATE

        # For Insert models, fields with defaults or auto-generated are optional
        if self.class_type == WriterClassType.INSERT and (c.has_default or c.is_generated):
            force_optional = True

        # Determine if type should be nullable
        make_nullable = c.is_nullable or self._null_defaults or force_optional
        col_dtype = f'{pyth_type}' + (' | None' if make_nullable else '')

        # field values
        field_values = dict()
        field_values_list_first = list()

        # Only add constraints for base model
        if self.class_type not in [WriterClassType.INSERT, WriterClassType.UPDATE]:
            if c.primary:
                field_values['primary_key'] = 'True'
            if c.is_unique:
                field_values['unique'] = 'True'
            # Add comment if available
            if hasattr(c, 'comment') and c.comment:
                field_values['comment'] = f'"{c.comment}"'
            for fk in self.table.foreign_keys:
                if c.name == fk.column_name:
                    field_values_list_first.append(f'ForeignKey("{fk.foreign_table_name}.{fk.foreign_column_name}")')

        # Always add nullable property if applicable
        if make_nullable:
            field_values['nullable'] = 'True'

        field_values_string = ', '.join(field_values_list_first) if len(field_values_list_first) > 0 else ''
        if len(field_values) > 0:
            if len(field_values_list_first) > 0:
                field_values_string += ', '
            field_values_string += ', '.join([f'{k}={v}' for k, v in field_values.items()])

        # Generate the column definition with cleaner formatting
        column_def = f'{c.name}: Mapped[{col_dtype}] = mapped_column({base_type}'
        if field_values_string:
            column_def += f', {field_values_string}'
        column_def += ')'

        return column_def

    def write_primary_keys(self) -> str | None:
        """Method to generate primary key definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.primary_keys]
        return AbstractClassWriter.column_section('Primary Keys', cols) if len(cols) > 0 else None

    def write_primary_columns(self) -> str | None:
        """Method to generate column definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.non_nullable + self.separated_columns.nullable]
        if len(cols) == 0:
            return None
        result: str = AbstractClassWriter.column_section('Columns', cols)
        return result

    def write_table_args(self) -> str | None:
        """Method to generate table arguments for the class.

        This method handles the table-level arguments like PrimaryKeyConstraint and schema.
        Originally part of write_foreign_columns, this was split out for better separation of concerns.
        """
        # Skip for insert and update models
        if self.class_type in [WriterClassType.INSERT, WriterClassType.UPDATE]:
            return None

        # Collect table arguments
        table_args = []

        # Add primary key constraints
        for con in self.table.constraints:
            if con.constraint_type() == 'PRIMARY KEY':
                primary_cols = ', '.join([f"'{c}'" for c in con.columns])
                name_str = f"name='{con.constraint_name}'"
                table_args.append(f'PrimaryKeyConstraint({primary_cols}, {name_str}),')

        # Add schema information
        # Use the actual schema from the table info instead of hardcoding 'public'
        table_args.append(f"{{ 'schema': '{self.schema}' }}")

        if table_args:
            table_args_str = '\t# Table Args\n\t__table_args__ = (\n'
            table_args_str += '\n'.join([f'\t\t{a}' for a in table_args]) + '\n\t)'
            return table_args_str
        return None

    def write_relationships(self) -> str | None:
        """Method to generate relationship definitions for the class.

        This method handles all SQLAlchemy relationship definitions, supporting:
        - ONE_TO_ONE: single instance (e.g., user: User | None)
        - ONE_TO_MANY: list of instances (e.g., posts: list[Post])
        - MANY_TO_MANY: list of instances (e.g., tags: list[Tag])

        Originally part of write_foreign_columns, this was split out for better separation of concerns.
        """
        relationships = []
        # Track generated relationship names to prevent duplicates
        relationship_names = set()

        # Add relationships from foreign keys
        for fk in self.table.foreign_keys:
            target_class = self._proper_name(fk.foreign_table_name)
            # Use exact class name for relationship name to ensure consistency
            rel_name = target_class.lower()

            # Pluralize name for one-to-many or many-to-many relationships
            if fk.relation_type != RelationType.ONE_TO_ONE:
                rel_name = pluralize(rel_name)

            # Skip if we've already processed this relationship
            if rel_name in relationship_names:
                continue
            relationship_names.add(rel_name)

            # Use exact table name for back reference
            back_ref = pluralize(self._proper_name(self.table.name).lower())
            if fk.relation_type == RelationType.ONE_TO_ONE:
                type_hint = f'Mapped[{target_class} | None]'
                rel_str = (
                    f'{rel_name}: {type_hint} = relationship('
                    f'"{target_class}", back_populates="{back_ref}", uselist=False)'
                )
            else:  # ONE_TO_MANY or MANY_TO_MANY
                type_hint = f'Mapped[list[{target_class}]]'
                rel_str = f'{rel_name}: {type_hint} = relationship("{target_class}", back_populates="{back_ref}")'

            relationships.append(rel_str)

        # Add relationships from relationships list
        if hasattr(self.table, 'relationships') and self.table.relationships:
            for rel in self.table.relationships:
                target_class = self._proper_name(rel.related_table_name)
                # Use exact class name for relationship name to ensure consistency
                rel_name = target_class.lower()

                # Pluralize name for one-to-many or many-to-many relationships
                if rel.relation_type != RelationType.ONE_TO_ONE:
                    rel_name = pluralize(rel_name)

                # Skip if we've already processed this relationship
                if rel_name in relationship_names:
                    continue
                relationship_names.add(rel_name)

                rel_type = rel.relation_type
                # Use exact table name for back reference
                back_ref = pluralize(self._proper_name(self.table.name).lower())

                if rel_type == RelationType.ONE_TO_ONE:
                    type_hint = f'Mapped[{target_class} | None]'
                    rel_str = (
                        f'{rel_name}: {type_hint} = relationship('
                        f'"{target_class}", back_populates="{back_ref}", uselist=False)'
                    )
                else:  # ONE_TO_MANY or MANY_TO_MANY
                    type_hint = f'Mapped[list[{target_class}]]'
                    rel_str = f'{rel_name}: {type_hint} = relationship("{target_class}", back_populates="{back_ref}")'

                relationships.append(rel_str)

        if relationships:
            rel_str = '\t# Relationships\n'
            rel_str += '\n'.join([f'\t{r}' for r in relationships])
            return rel_str
        return None

    def write_operational_class(self) -> str | None:
        """Method to generate operational class definitions."""
        return None

    def write_foreign_columns(self, use_base: bool = False) -> str | None:
        """Method to generate foreign column definitions for the class.

        DEVELOPER NOTE:
        This method is deprecated and only maintained for test compatibility.
        Its functionality has been split into two more focused methods:
        - write_table_args: Handles table-level arguments
        - write_relationships: Handles SQLAlchemy relationship definitions

        New code should use write_table_args() and write_relationships() directly instead.
        This method may be removed in a future version.
        """
        sections = []
        table_args = self.write_table_args()
        relationships = self.write_relationships()

        if table_args:
            sections.append(table_args)
        if relationships:
            sections.append(relationships)

        result = '\n\n'.join(sections) if sections else None
        return result + '\n' if result else None

    def write_columns(self, add_fk: bool = False) -> str:
        """Method to generate column definitions for the class."""
        keys = self.write_primary_keys()
        cols = self.write_primary_columns()

        columns = [x for x in [keys, cols] if x is not None]
        result = '\n\n'.join(columns)
        return result + '\n' if result else ''

    def write_class(self, add_fk: bool = False) -> str:
        """Method to generate the class definition."""
        name = self.write_name()
        metaclass = self.write_metaclass()
        docs = self.write_docs()
        cols = self.write_columns(add_fk)
        relationships = self.write_relationships()
        table_args = self.write_table_args()

        # Build class definition
        parts = []

        # Class declaration
        class_decl = f'class {name}'
        if metaclass is not None:
            class_decl += f'({metaclass})'
        class_decl += ':'
        class_decl += docs or '\n\t"""Base class."""'
        parts.append(class_decl)

        # Add extra newline for better spacing
        parts.append('')

        # Class body
        if cols is not None:
            parts.append(cols.rstrip())  # Remove trailing newlines
        if relationships is not None:
            # Add extra spacing before relationships
            parts.append('')  # Empty line for spacing
            parts.append(relationships.rstrip())  # Remove trailing newlines
        if table_args is not None:
            # Add extra spacing before table args
            parts.append('')  # Empty line for spacing
            parts.append(table_args.rstrip())  # Remove trailing newlines

        return '\n'.join(parts)


class SqlAlchemyFastAPIWriter(AbstractFileWriter):
    def __init__(
        self,
        tables: list[TableInfo],
        file_path: str,
        writer: type[AbstractClassWriter] = SqlAlchemyFastAPIClassWriter,
        add_null_parent_classes: bool = False,
        singular_names: bool = False,
        database_type: DatabaseType = DatabaseType.POSTGRES,
    ):
        super().__init__(tables, file_path, writer, add_null_parent_classes, singular_names, database_type)

    def write(self) -> str:
        """Override the base write method to handle newlines correctly."""
        parts = [
            self.write_imports(),
            self.write_custom_classes(),
            self.write_base_classes(),
            self.write_operational_classes(),
        ]
        result: str = self.jstr.join(p for p in parts if p is not None)
        return result

    def _dt_imports(
        self, imports: set, default_import: tuple[Any, Any | None] = ('String,str', 'from sqlalchemy import String')
    ) -> None:
        """Update the imports with the necessary data types."""

        def _pyi(c: ColumnInfo) -> str | None:  # pyi = pydantic import  # noqa
            import_stmt: str | None = get_sqlalchemy_v2_type(
                c.post_gres_datatype, database_type=self.database_type, default=default_import
            )[2]
            # print(f'import_stmt: {import_stmt}')
            return import_stmt

        # column data types
        imports.update(filter(None, map(_pyi, (c for t in self.tables for c in t.columns))))

    def write_imports(self) -> str:
        """Method to generate the imports for the file."""
        # standard
        imports = {
            'from __future__ import annotations',
            '',
            'from sqlalchemy import ForeignKey',
            'from sqlalchemy.orm import DeclarativeBase',
            'from sqlalchemy.orm import Mapped',
            'from sqlalchemy.orm import mapped_column',
            'from sqlalchemy.orm import relationship',
        }
        if any([len(t.primary_key()) > 0 for t in self.tables]):
            imports.add('from sqlalchemy import PrimaryKeyConstraint')

        # Add Enum import if any enum columns exist
        if any(c.enum_info is not None for t in self.tables for c in t.columns):
            imports.add('from sqlalchemy import Enum')
            imports.add('from enum import Enum as PyEnum, auto')

        # Add TIMESTAMP import if any timestamp with timezone columns exist
        if any('with time zone' in c.post_gres_datatype.lower() for t in self.tables for c in t.columns):
            imports.add('from sqlalchemy.dialects.postgresql import TIMESTAMP')

        # column data types
        self._dt_imports(imports)

        new_imports = set()
        for i in imports:
            new_imports.update(i.split('\n'))

        return '\n'.join(sorted(new_imports))

    def _class_writer_helper(
        self,
        comment_title: str,
        comments: list[str] = [],
        classes_override: list[str] = [],
        is_base: bool = True,
        **kwargs: Any,
    ) -> str:
        sxn = get_section_comment(comment_title, comments)
        classes = classes_override
        if len(classes_override) == 0:
            attr = 'write_class' if is_base else 'write_operational_class'

            def _method(t: TableInfo) -> Any:
                writer_instance = self.writer(t, database_type=self.database_type, singular_names=self.singular_names)
                return getattr(writer_instance, attr)

            if 'add_fk' in kwargs:
                classes = [_method(t)(add_fk=kwargs['add_fk']) for t in self.tables]
            else:
                classes = [_method(t)() for t in self.tables]

        result: str = self.join([sxn, *classes])
        return result

    def _collect_enum_infos(self) -> list[EnumInfo]:
        """Collect all unique enum infos from all tables."""
        enum_infos = {}
        for table in self.tables:
            for column in table.columns:
                if column.enum_info is not None:
                    enum_key = f'{column.enum_info.schema}.{column.enum_info.name}'
                    if enum_key not in enum_infos:
                        enum_infos[enum_key] = column.enum_info
        return list(enum_infos.values())

    def _generate_enum_classes(self) -> list[str]:
        """Generate Python enum classes for database enum types."""
        enum_classes: list[str] = []
        enum_infos = self._collect_enum_infos()

        if not enum_infos:
            return enum_classes

        for enum_info in enum_infos:
            class_name = enum_info.python_class_name()
            enum_class = [f'class {class_name}(PyEnum):', f'\t"""Enum for {enum_info.schema}.{enum_info.name}."""']

            # Add enum members
            for value in enum_info.values:
                member_name = value.upper()
                enum_class.append(f"\t{member_name} = '{value}'")

            enum_classes.append('\n'.join(enum_class))
        return enum_classes

    def write_custom_classes(self, add_fk: bool = False) -> str:
        """Method to write the complete class definition."""
        classes = []

        # Generate enum classes first
        enum_classes = self._generate_enum_classes()
        if enum_classes:
            enums_section = get_section_comment('Enum Classes', ['Database enum types as Python classes'])
            classes.extend([enums_section] + enum_classes)

        # Add base class
        declarative_base_class = (
            'class Base(DeclarativeBase):\n\t"""Declarative Base Class."""\n\t# type_annotation_map = {}\n\n\tpass'
        )
        base_section = get_section_comment('Declarative Base', [])
        classes.extend([base_section, declarative_base_class])

        return '\n\n'.join(classes)

    def write_base_classes(self) -> str:
        """Method to write the base classes."""
        return self._class_writer_helper('Base Classes')

    def write_operational_classes(self) -> str | None:
        """Method to write the operational classes.

        This includes Insert and Update models that follow the CRUD pattern.
        """
        # Generate Insert models
        insert_models = self._generate_crud_models(WriterClassType.INSERT, 'Insert Models')

        # Generate Update models
        update_models = self._generate_crud_models(WriterClassType.UPDATE, 'Update Models')

        # Combine them if any exist
        parts = []
        if insert_models:
            parts.append(insert_models)
        if update_models:
            parts.append(update_models)

        return '\n\n'.join(parts) if parts else None

    def _generate_crud_models(self, class_type: WriterClassType, title: str) -> str | None:
        """Helper method to generate CRUD models (Insert or Update)."""
        comments = []
        if class_type == WriterClassType.INSERT:
            comments.extend(
                [
                    'Models for inserting new records',
                    'These models exclude auto-generated fields and make fields with defaults optional',
                    'Use these models when creating new database entries',
                ]
            )
        elif class_type == WriterClassType.UPDATE:
            comments.extend(
                [
                    'Models for updating existing records',
                    'All fields are optional to support partial updates',
                    'Use these models for PATCH/PUT operations to modify existing records',
                ]
            )

        classes = []
        for table in self.tables:
            # Create writer with the specified class type
            writer = self.writer(
                table,
                class_type=class_type,
                database_type=self.database_type,
                singular_names=self.singular_names,
            )
            class_def = writer.write_class()
            if class_def:
                classes.append(class_def)

        if not classes:
            return None

        return self._class_writer_helper(comment_title=title, comments=comments, classes_override=classes)
