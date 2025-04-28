import logging
import re
from functools import partial
from typing import Any

from inflection import pluralize

from supabase_pydantic.util.constants import CUSTOM_MODEL_NAME, RelationType, WriterClassType
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, SortedColumns, TableInfo
from supabase_pydantic.util.marshalers import column_name_reserved_exceptions, string_is_reserved
from supabase_pydantic.util.util import get_pydantic_type
from supabase_pydantic.util.writers.abstract_classes import AbstractClassWriter, AbstractFileWriter
from supabase_pydantic.util.writers.util import get_base_class_post_script as post
from supabase_pydantic.util.writers.util import get_section_comment

# FastAPI


class PydanticFastAPIClassWriter(AbstractClassWriter):
    def __init__(
        self,
        table: TableInfo,
        class_type: WriterClassType = WriterClassType.BASE,
        null_defaults: bool = False,
        generate_enums: bool = True,
    ):
        super().__init__(table, class_type, null_defaults)
        self.generate_enums = generate_enums
        self.separated_columns: SortedColumns = self.table.sort_and_separate_columns(
            separate_nullable=False, separate_primary_key=True
        )

    def write_name(self) -> str:
        """Method to generate the header for the base class."""
        base_name = self.name
        result = base_name

        # Add appropriate suffix for different model types
        if self.class_type == WriterClassType.INSERT:
            result = f'{base_name}Insert'
        elif self.class_type == WriterClassType.UPDATE:
            result = f'{base_name}Update'
        elif self.class_type == WriterClassType.BASE:
            result = f'{base_name}BaseSchema'
        else:
            result = base_name

        # print(f'write_name() for {self.table.name}:')
        # print(f'  class_type: {self.class_type}')
        # print(f'  base_name: {base_name}')
        # print(f'  result: {result}')
        return result

    def write_metaclass(self, metaclasses: list[str] | None = None) -> str | None:
        """Method to generate the metaclasses for the class.

        Args:
            metaclasses: Optional list of metaclasses to use. If provided, these will be joined
                        with commas and returned directly. If not provided, the appropriate
                        model type will be returned based on class_type.
        """
        # If metaclasses are provided, join them with commas and return
        if metaclasses:
            return ', '.join(metaclasses)

        # Otherwise, determine the appropriate model type based on class_type
        if self.class_type == WriterClassType.INSERT:
            return f'{CUSTOM_MODEL_NAME}Insert'
        elif self.class_type == WriterClassType.UPDATE:
            return f'{CUSTOM_MODEL_NAME}Update'
        elif self.class_type in [WriterClassType.BASE, WriterClassType.PARENT]:
            return CUSTOM_MODEL_NAME
        elif self.class_type == WriterClassType.BASE_WITH_PARENT:
            return f'{self.name}{post(self.table.table_type, WriterClassType.PARENT)}'
        else:
            return CUSTOM_MODEL_NAME

    def _parse_length_constraint(self, constraint_def: str | None) -> dict[str, int] | None:
        """Parse length constraints from a CHECK constraint definition.

        Args:
            constraint_def: SQL constraint definition string

        Returns:
            Dictionary with min_length and/or max_length if constraints found, None otherwise
        """
        if not constraint_def:
            return None

        length_pattern = r'length\((\w+)\)\s*([=<>]+)\s*(\d+)'
        matches = re.findall(length_pattern, constraint_def)

        if not matches:
            return None

        result = {}
        for _, operator, value in matches:
            value = int(value)
            if operator == '=':
                result['min_length'] = value
                result['max_length'] = value
            elif operator == '>=':
                result['min_length'] = value
            elif operator == '<=':
                result['max_length'] = value

        return result if result else None

    def _get_optional_reason(self, c: ColumnInfo) -> str | None:
        """Get the reason why a field is optional."""
        reasons = []
        if c.is_nullable:
            reasons.append('nullable')
        if c.has_default:
            reasons.append('has default value')
        if c.is_generated:
            reasons.append('auto-generated')
        return ', '.join(reasons) if reasons else None

    def write_column(self, c: ColumnInfo, add_comment: bool = True) -> str:
        """Write a column definition for a Pydantic model."""
        # Skip auto-generated fields for Insert and Update models
        if (self.class_type in [WriterClassType.INSERT, WriterClassType.UPDATE]) and c.is_identity:
            return ''

        # Use enum class as type if this is an enum column, unless generate_enums is False
        if self.generate_enums and getattr(c, 'enum_info', None) is not None and c.enum_info is not None:
            base_type = c.enum_info.python_class_name()
        else:
            base_type = get_pydantic_type(c.post_gres_datatype, ('str', None))[0]

        # For Update models, all fields are optional
        force_optional = self.class_type == WriterClassType.UPDATE

        # For Insert models:
        # - Fields with defaults are optional
        # - Required fields without defaults stay required
        # - Nullable fields are optional and nullable
        if self.class_type == WriterClassType.INSERT:
            if c.has_default or c.is_generated:
                force_optional = True

        # Get the reason why field is optional (will be added as comment)
        comment = None
        if force_optional or c.is_nullable or self._null_defaults:
            reason = (
                self._get_optional_reason(c) if self.class_type == WriterClassType.INSERT else 'optional for updates'
            )
            comment = reason

        # Handle length constraints for text fields
        length_constraints = None
        if c.post_gres_datatype.lower() == 'text' and c.constraint_definition:
            length_constraints = self._parse_length_constraint(c.constraint_definition)

        # Build the type annotation
        if length_constraints and base_type == 'str':
            constraints = {}
            if 'min_length' in length_constraints:
                constraints['min_length'] = length_constraints['min_length']
            if 'max_length' in length_constraints:
                constraints['max_length'] = length_constraints['max_length']

            type_str = f'Annotated[str, StringConstraints(**{constraints})]'
        else:
            type_str = base_type

        # Add nullable type if needed
        type_str = f'{type_str} | None' if (c.is_nullable or self._null_defaults or force_optional) else type_str

        # Build field values
        field_values = {}
        if (c.is_nullable is not None and c.is_nullable) or self._null_defaults or force_optional:
            field_values['default'] = 'None'
        if c.alias is not None:
            field_values['alias'] = f'"{c.alias}"'

        # Construct the final column definition
        col = f'{c.name}: {type_str}'
        if field_values:
            col += ' = Field(' + ', '.join([f'{k}={v}' for k, v in field_values.items()]) + ')'

        # Add comment about field properties if present and requested
        if comment and add_comment and self.class_type == WriterClassType.INSERT:
            col += f'  # {comment}'

        return col

    def write_docs(self) -> str:
        """Method to generate the docstrings for the class."""
        if self.class_type == WriterClassType.INSERT:
            qualifier = 'Insert'
        elif self.class_type == WriterClassType.UPDATE:
            qualifier = 'Update'
        else:
            qualifier = '(Nullable) Parent' if self._null_defaults else 'Base'
        return f'\n\t"""{self.name} {qualifier} Schema."""\n\n'

    def write_primary_keys(self) -> str | None:
        """Method to generate primary key definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.primary_keys]
        return AbstractClassWriter.column_section('Primary Keys', cols) if len(cols) > 0 else None

    def write_primary_columns(self) -> str | None:
        """Method to generate column definitions for the class."""
        # For Insert and Update models, organize fields by required/optional
        if self.class_type in [WriterClassType.INSERT, WriterClassType.UPDATE]:
            required_fields = []
            optional_fields = []
            field_comments = []
            primary_key_comments = []

            # First gather all field properties
            for c in self.separated_columns.primary_keys + self.separated_columns.remaining:
                if c.is_identity:
                    if self.class_type == WriterClassType.INSERT:
                        primary_key_comments.append(f'# {c.name}: auto-generated')
                    continue

                if c.has_default or c.is_generated or c.is_nullable:
                    reason = self._get_optional_reason(c)
                    if reason:
                        if c in self.separated_columns.primary_keys:
                            primary_key_comments.append(f'# {c.name}: {reason}')
                        else:
                            field_comments.append(f'# {c.name}: {reason}')

            # Then organize fields by required/optional
            for c in self.separated_columns.remaining:
                # Skip identity columns for Insert/Update
                if c.is_identity:
                    continue

                # For Update models, all fields are optional
                if self.class_type == WriterClassType.UPDATE:
                    optional_fields.append(c)
                # For Insert models, organize based on optionality
                else:
                    if c.has_default or c.is_generated or c.is_nullable:
                        optional_fields.append(c)
                    else:
                        required_fields.append(c)

            sections = []
            if field_comments and self.class_type in [WriterClassType.INSERT, WriterClassType.UPDATE]:
                sections.extend(['\t# Field properties:', *field_comments, ''])

            if required_fields:
                sections.extend(
                    ['# Required fields', *[self.write_column(c, add_comment=False) for c in required_fields]]
                )
            if optional_fields:
                if required_fields:  # Add spacing between sections
                    sections.append('')
                sections.extend(
                    ['\t# Optional fields', *[self.write_column(c, add_comment=False) for c in optional_fields]]
                )
            return '\n\t'.join(sections) if sections else None

        # For base models, keep original ordering
        cols = [self.write_column(c) for c in self.separated_columns.remaining]
        if len(cols) == 0:
            return None
        return AbstractClassWriter.column_section('Columns', cols)

    def write_foreign_columns(self, use_base: bool = True) -> str | None:
        """Method to generate foreign column definitions for the class.

        The type hint for each foreign key depends on the relationship type:
        - ONE_TO_ONE: single instance (e.g., author: User | None)
        - ONE_TO_MANY: list of instances (e.g., posts: list[Post] | None)
        - MANY_TO_MANY: list of instances (e.g., tags: list[Tag] | None)

        Field naming follows these conventions:
        - ONE_TO_ONE: use foreign table name (e.g., author)
        - ONE_TO_MANY/MANY_TO_MANY: use pluralized foreign table name (e.g., posts)
        """
        _n = AbstractClassWriter._proper_name

        def _col(x: ForeignKeyInfo) -> str:
            # Get the target table name in proper case for type hint
            target_type = _n(x.foreign_table_name)

            # Base field name on the foreign table name, not the column name
            # This prevents naming conflicts and is more semantic
            base_field_name = x.foreign_table_name.lower()

            # Determine type hint and field name based on relationship type
            logging.debug('=' * 80)
            logging.debug(f'Processing foreign key {x.column_name} -> {x.foreign_table_name}.{x.foreign_column_name}')
            logging.debug(f'  Relationship type from analysis: {x.relation_type}')
            logging.debug('  Foreign key details:')
            logging.debug(f'    Column name: {x.column_name}')
            logging.debug(f'    Foreign table: {x.foreign_table_name}')
            logging.debug(f'    Foreign column: {x.foreign_column_name}')

            # Handle relationships based on whether we're looking at the source or target table
            # Source table = table that has the foreign key (e.g., file has project_id)
            # Target table = table being referenced (e.g., project is referenced by file)

            # If we're generating the model for the table that has the foreign key,
            # then we're the source. Otherwise, we're the target.
            # Example: if we're generating File model and see project_id -> project.id,
            # then we're the source because we have the foreign key.
            table_name = self.table.name.lower()
            we_have_foreign_key = x.column_name.endswith('_id')

            logging.debug('  Current context:')
            logging.debug(f'    Table being generated: {table_name}')
            logging.debug(f'    We have foreign key: {we_have_foreign_key} (column ends with _id)')

            # Check if this is a self-referential relationship
            is_self_ref = x.foreign_table_name.lower() == table_name

            # For self-referential relationships, check if there's a matching relationship
            # that indicates the true nature of the relationship
            if is_self_ref:
                # Look for a matching relationship to determine the true type
                for rel in self.table.relationships:
                    if rel.related_table_name.lower() == table_name:
                        x.relation_type = rel.relation_type
                        break

            if x.relation_type == RelationType.ONE_TO_ONE:
                # ONE_TO_ONE is symmetric, so it's the same from both sides
                type_hint = target_type
                field_name = base_field_name
                logging.debug(f'  Using ONE_TO_ONE: {field_name}: {type_hint}')
            elif x.relation_type == RelationType.MANY_TO_ONE:
                if we_have_foreign_key:
                    # We have a foreign key pointing to another table
                    # e.g., File has project_id pointing to Project
                    # So we reference a single instance
                    type_hint = target_type
                    field_name = base_field_name
                    logging.debug(f'  Using MANY_TO_ONE (we have the foreign key): {field_name}: {type_hint}')
                else:
                    # Another table has a foreign key pointing to us
                    # e.g., Project being referenced by File.project_id
                    # So we'll have many records pointing to us
                    type_hint = f'list[{target_type}]'
                    field_name = pluralize(base_field_name)
                    logging.debug(f'  Using ONE_TO_MANY (they have the foreign key): {field_name}: {type_hint}')
            elif x.relation_type == RelationType.ONE_TO_MANY:
                if we_have_foreign_key:
                    # We have a foreign key pointing to another table
                    # So we reference a single instance
                    type_hint = target_type
                    field_name = base_field_name
                    logging.debug(f'  Using MANY_TO_ONE (we have the foreign key): {field_name}: {type_hint}')
                else:
                    # Another table has a foreign key pointing to us
                    # So we'll have many records pointing to us
                    type_hint = f'list[{target_type}]'
                    field_name = pluralize(base_field_name)
                    logging.debug(f'  Using ONE_TO_MANY (they have the foreign key): {field_name}: {type_hint}')
            else:  # MANY_TO_MANY
                type_hint = f'list[{target_type}]'
                field_name = pluralize(base_field_name)
                logging.debug(f'  Using list type: {field_name}: {type_hint}')

            return f'{field_name}: {type_hint} | None = Field(default=None)'

        # Track used field names to prevent duplicates
        used_fields = set()
        fks = []

        # Generate foreign key fields
        for fk in self.table.foreign_keys:
            field_def = _col(fk)
            field_name = field_def.split(':')[0].strip()

            # Skip duplicate field names
            if field_name not in used_fields:
                used_fields.add(field_name)
                fks.append(field_def)

        # Add relationship fields that aren't covered by foreign keys
        for rel in self.table.relationships:
            # For self-referential tables, we want both the foreign key and relationship fields
            # For other tables, skip if this relationship is already covered by a foreign key
            is_self_ref = rel.related_table_name.lower() == self.table.name.lower()
            if not is_self_ref and any(
                fk.foreign_table_name == rel.related_table_name for fk in self.table.foreign_keys
            ):
                continue

            target_type = _n(rel.related_table_name)
            field_name = pluralize(rel.related_table_name.lower())  # Always pluralize for relationships

            # Skip if field name already used
            if field_name not in used_fields:
                used_fields.add(field_name)
                type_hint = f'list[{target_type}]'
                fks.append(f'{field_name}: {type_hint} | None = Field(default=None)')

        return AbstractClassWriter.column_section('Foreign Keys', fks) if len(fks) > 0 else None

    def write_operational_class(self) -> str | None:
        """Method to generate operational class definitions."""
        # Create a base schema writer and get its name
        base_writer = PydanticFastAPIClassWriter(self.table, WriterClassType.BASE, generate_enums=self.generate_enums)
        m = base_writer.write_name()
        op_class = [
            f'class {self.name}({m}):',
            f'\t"""{self.name} Schema for Pydantic.',
            f'\n\tInherits from {m}. Add any customization here.',
            '\t"""',
        ]
        if len(self.table.foreign_keys) > 0:
            fcols = self.write_foreign_columns(use_base=False)
            if fcols is not None:
                op_class.append('\n' + fcols)
        else:  # add a pass statement if there are no foreign keys
            op_class.append('\tpass')

        return '\n'.join(op_class)


class PydanticFastAPIWriter(AbstractFileWriter):
    def __init__(
        self,
        tables: list[TableInfo],
        file_path: str,
        writer: type[AbstractClassWriter] = PydanticFastAPIClassWriter,
        add_null_parent_classes: bool = False,
        generate_crud_models: bool = True,
        generate_enums: bool = True,
    ):
        # Developer's Note:
        # Use functools.partial to wrap the writer so that it always
        # receives the correct extra arguments, but only if the concrete
        # class supports them.
        writer_with_enums = partial(writer, generate_enums=generate_enums)  # type: ignore

        super().__init__(tables, file_path, writer_with_enums, add_null_parent_classes)
        self.generate_crud_models = generate_crud_models
        self.generate_enums = generate_enums

    def _dt_imports(self, imports: set, default_import: tuple[Any, Any | None] = (Any, None)) -> None:
        """Update the imports with the necessary data types."""

        def _pyi(c: ColumnInfo) -> str | None:  # pyi = pydantic import  # noqa
            return get_pydantic_type(c.post_gres_datatype, default_import)[1]

        # column data types
        imports.update(filter(None, map(_pyi, (c for t in self.tables for c in t.columns))))

    def write_imports(self) -> str:
        """Method to generate the imports for the file."""
        # standard
        imports = {
            'from pydantic import BaseModel',
            'from pydantic import Field',
            'from pydantic.types import StringConstraints',
        }
        if any([len(t.table_dependencies()) > 0 for t in self.tables]):
            imports.add('from __future__ import annotations')

        # Check if any column uses an enum type
        if self.generate_enums and any(
            any(getattr(c, 'enum_info', None) is not None for c in t.columns) for t in self.tables
        ):
            imports.add('from enum import Enum')

        # Check if Annotated is needed (used with StringConstraints for text columns with length constraints)
        # Look for text columns with constraint definitions containing 'length' function
        needs_annotated = any(
            any(
                c.post_gres_datatype.lower() == 'text'
                and c.constraint_definition
                and 'length(' in c.constraint_definition.lower()
                for c in t.columns
            )
            for t in self.tables
        )
        if needs_annotated:
            imports.add('from typing import Annotated')

        # column data types
        self._dt_imports(imports)

        return '\n'.join(sorted(imports))

    def _class_writer_helper(
        self,
        comment_title: str,
        comments: list[str] = [],
        classes_override: list[str] = [],
        is_base: bool = True,
        class_type: WriterClassType = WriterClassType.BASE,
        **kwargs: Any,
    ) -> str:
        # print(f'\n=== Generating {comment_title} ===\nClass type: {class_type}')
        sxn = get_section_comment(comment_title, comments)
        classes = classes_override

        if len(classes_override) == 0:
            attr = 'write_class' if is_base else 'write_operational_class'

            def _method(t: TableInfo) -> Any:
                writer = None
                if class_type == WriterClassType.PARENT:
                    writer = self.writer(t, class_type, True, generate_enums=self.generate_enums)
                elif class_type == WriterClassType.BASE_WITH_PARENT:
                    writer = self.writer(t, class_type, False, generate_enums=self.generate_enums)
                else:
                    writer = self.writer(t, class_type, generate_enums=self.generate_enums)  # Pass class_type here

                # print(f'\nTable: {t.name}')
                # print(f'Class type: {class_type}')
                # print(f'Writer class: {writer.__class__.__name__}')
                # print(f'Method: {attr}')

                return getattr(writer, attr)

            if len(kwargs) > 0:
                classes = [_method(t)(**kwargs) for t in self.tables]
            else:
                classes = [_method(t)() for t in self.tables]

        return self.join([sxn, *classes])

    def write_enum_types(self) -> str | None:
        """Generate a section of Python Enum classes for all unique enums used in the schema."""
        if not getattr(self, 'generate_enums', True):
            return None
        # Collect all EnumInfo objects from all columns in all tables
        enums = {}
        for table in self.tables:
            for col in table.columns:
                enum_info = getattr(col, 'enum_info', None)
                if enum_info:
                    # Use (schema, name) as a unique key to avoid duplicates
                    key = (enum_info.schema, enum_info.name)
                    enums[key] = enum_info

        if not enums:
            return None

        # Build the section string
        lines = ['# ENUM TYPES', '# These are generated from Postgres user-defined enum types.\n']
        for enum in enums.values():
            lines.append(f'class {enum.python_class_name()}(str, Enum):')
            for value in enum.values:
                member = enum.python_member_name(value)
                comment = ''
                if string_is_reserved(member.lower()) or column_name_reserved_exceptions(member.lower()):
                    member = f'{member.upper()}_'
                    comment = f'  # Note: original name was {value} (reserved keyword)'
                lines.append(f'\t{member.upper()} = "{value}"{comment}')
            lines.append('')  # Blank line after each enum

        return '\n'.join(lines)

    def write_custom_classes(self) -> str | None:
        """Method to generate the custom classes for the file."""
        b = 'BaseModel'
        classes = [
            f'class {CUSTOM_MODEL_NAME}({b}):\n\t"""Base model class with common features."""\n\tpass',
        ]

        if self.generate_crud_models:
            classes.extend(
                [
                    f'class {CUSTOM_MODEL_NAME}Insert({CUSTOM_MODEL_NAME}):\n\t"""Base model for insert operations with common features."""\n\tpass',  # noqa: E501
                    f'class {CUSTOM_MODEL_NAME}Update({CUSTOM_MODEL_NAME}):\n\t"""Base model for update operations with common features."""\n\tpass',  # noqa: E501
                ]
            )

        return self._class_writer_helper(
            comment_title='Custom Classes',
            comments=['These are custom model classes for defining common features among Pydantic Base Schema.'],
            classes_override=classes,
        )

    def write_base_classes(self) -> str:
        """Method to generate the base, insert, and update classes for the file."""
        classes = []

        # Generate parent classes if needed
        if self.add_null_parent_classes:
            classes.append(
                self._class_writer_helper(
                    'Parent Classes',
                    comments=[
                        'This is a parent class with all fields as nullable. This is useful for refining your models with inheritance. See https://stackoverflow.com/a/65907609.'  # noqa: E501
                    ],
                    class_type=WriterClassType.PARENT,
                )
            )
            base_class_type = WriterClassType.BASE_WITH_PARENT
        else:
            base_class_type = WriterClassType.BASE

        # Generate base (Row) classes
        classes.append(
            self._class_writer_helper(
                'Base Classes',
                comments=['These are the base Row models that include all fields.'],
                class_type=base_class_type,
            )
        )

        if self.generate_crud_models:
            # Generate Insert classes
            classes.append(
                self._class_writer_helper(
                    'Insert Classes',
                    comments=[
                        'These models are used for insert operations. Auto-generated fields (like IDs and timestamps) are optional.'  # noqa: E501
                    ],
                    class_type=WriterClassType.INSERT,
                )
            )

            # Generate Update classes
            classes.append(
                self._class_writer_helper(
                    'Update Classes',
                    comments=['These models are used for update operations. All fields are optional.'],
                    class_type=WriterClassType.UPDATE,
                )
            )

        return '\n'.join(c for c in classes if c)

    def write_operational_classes(self) -> str | None:
        """Method to generate the operational classes for the file."""
        return self._class_writer_helper('Operational Classes', is_base=False)

    def write(self) -> str:
        """Override to include enum types after imports and before custom classes."""
        parts = [
            self.write_imports(),
            self.write_enum_types(),
            self.write_custom_classes(),
            self.write_base_classes(),
            self.write_operational_classes(),
        ]

        # filter None and join parts using self.jstr (which is '\\n\\n\\n')
        return self.jstr.join(p for p in parts if p is not None) + '\n'
