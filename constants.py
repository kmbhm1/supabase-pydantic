import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from random import random

from faker import Faker

# Dataclasses


class RelationType(str, Enum):
    ONE_TO_ONE = 'One-to-One'
    ONE_TO_MANY = 'One-to-Many'
    MANY_TO_MANY = 'Many-to-Many'


def generate_fake_data(datatype: str, max_length: int | None = None, fake: Faker = Faker()):
    """Generate fake data based on the datatype."""
    if datatype == 'integer':
        return fake.random_int(min=1, max=1000)
    elif datatype == 'varchar' or datatype == 'text':
        return fake.text(max_nb_chars=max_length) if max_length else fake.text()
    elif datatype == 'boolean':
        return fake.boolean()
    elif datatype == 'datetime':
        return fake.date_time()
    elif datatype == 'uuid':
        return str(fake.uuid4())
    # Add more datatypes as needed
    else:
        return None


@dataclass
class AsDictParent:
    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)


@dataclass
class ColumnInfo(AsDictParent):
    name: str
    post_gres_datatype: str
    datatype: str
    default: str | None = None
    is_nullable: bool | None = True
    max_length: int | None = None

    def __str__(self) -> str:
        return json.dumps(asdict(self), indent=4)


@dataclass
class ForeignKeyInfo(AsDictParent):
    constraint_name: str
    column_name: str
    foreign_table_name: str
    foreign_column_name: str
    relation_type: RelationType  # E.g., "One-to-One", "One-to-Many"
    foreign_table_schema: str = 'public'


@dataclass
class TableInfo(AsDictParent):
    name: str
    schema: str = 'public'
    columns: list[ColumnInfo] = field(default_factory=list)
    foreign_keys: list[ForeignKeyInfo] = field(default_factory=list)

    def add_column(self, column: ColumnInfo):
        """Add a column to the table."""
        self.columns.append(column)

    def add_foreign_key(self, fk: ForeignKeyInfo):
        """Add a foreign key to the table."""
        self.foreign_keys.append(fk)

    def sort_and_combine_columns_for_pydantic_model(self):
        """Sort and combine columns based on is_nullable attribute."""
        # Split the columns based on is_nullable attribute
        nullable_columns = [column for column in self.columns if column.is_nullable]
        non_nullable_columns = [column for column in self.columns if not column.is_nullable]

        # Sort each list alphabetically by column name
        nullable_columns.sort(key=lambda x: x.name)
        non_nullable_columns.sort(key=lambda x: x.name)

        # Combine them with non-nullable first
        combined_columns = non_nullable_columns + nullable_columns
        return combined_columns

    def generate_fake_row(self):
        """Generate a dictionary with column names as keys and fake data as values."""
        row = {}
        fake = Faker()
        for column in self.columns:
            if column.is_nullable and random.random() < 0.1:
                row[column.name] = None
            else:
                row[column.name] = generate_fake_data(column.datatype, column.max_length, fake)
        return row


pydantic_type_map = {
    'integer': ('int', None),
    'bigint': ('int', None),
    'smallint': ('int', None),
    'numeric': ('float', None),
    'text': ('str', None),
    'varchar': ('str', None),
    'boolean': ('bool', None),
    'timestamp': ('datetime', 'from datetime import datetime'),
    'timestamp with time zone': ('datetime', 'from datetime import datetime'),
    'timestamp without time zone': ('datetime', 'from datetime import datetime'),
    'date': ('datetime.date', 'from datetime import date'),
    'uuid': ('UUID4', 'from uuid import UUID4'),
    'json': ('dict', None),
    'jsonb': ('dict', None),
    'character varying': ('str', None),
    'ARRAY': ('list', None),
    # Add more data types and their imports as necessary.
}


# Queries

GET_TABLE_COLUMN_DETAILS = """
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    tc.constraint_name
FROM
    information_schema.table_constraints AS tc
JOIN
    information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN
    information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public';
"""

GET_ALL_PUBLIC_TABLES_AND_COLUMNS = """
SELECT
    c.table_schema,
    c.table_name,
    c.column_name,
    c.column_default,
    c.is_nullable,
    c.data_type,
    c.character_maximum_length
FROM
    information_schema.columns AS c
JOIN
    information_schema.tables AS t ON c.table_name = t.table_name AND c.table_schema = t.table_schema
WHERE
    c.table_schema = 'public'
    AND t.table_type = 'BASE TABLE'
ORDER BY
    c.table_schema, c.table_name, c.ordinal_position;
"""
