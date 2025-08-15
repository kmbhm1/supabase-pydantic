import logging
from collections.abc import Callable, Generator
from itertools import islice, product
from math import inf, prod
from random import choice, randint
from typing import Any

from supabase_pydantic.db.graph import sort_tables_for_insert
from supabase_pydantic.db.models import ColumnInfo, TableInfo
from supabase_pydantic.db.seed.fake import format_for_postgres, generate_fake_data, guess_datetime_order

# Get Logger
logger = logging.getLogger(__name__)


# Maximum number of rows to generate
MAX_ROWS = 200


def total_possible_combinations(table: TableInfo) -> float:
    """Get the number of maximum rows for a table based on the unique rows."""
    if not table.has_unique_constraint():
        return inf

    values = []
    for c in table.columns:
        if c.is_unique:
            if c.user_defined_values:
                values.append(len(c.user_defined_values))  # Only add the length if there are user defined values.
            else:
                return inf  # If any unique column doesn't have defined values, the possibilities are infinite.

    return float(prod(values))  # Ensure that the product is in float to handle large numbers properly.


def random_num_rows() -> int:
    """Generate a random number of rows."""
    return randint(10, MAX_ROWS)


def pick_random_foreign_key(column_name: str, table: TableInfo, remember_fn: Callable) -> Any:
    """Pick a random foreign key value for a column."""
    fk = next((fk for fk in table.foreign_keys if fk.column_name == column_name), None)
    if fk is None:
        # TODO: change this to debug logging
        # print(f'Could not find foreign table for column {column_name}')
        return 'NULL'
    else:
        try:
            values = remember_fn(fk.foreign_table_name, fk.foreign_column_name)
            return choice(list(values))
        except KeyError:
            # TODO: change this to debug logging
            # print(f'Could not find foreign table for column {column_name}')
            return 'NULL'


def unique_data_rows(table: TableInfo, remember_fn: Callable) -> list[dict[str, Any]]:
    """Generate unique data rows for a table based on the unique columns."""
    if not table.has_unique_constraint():
        return []

    # Get the unique columns, in order
    # names, values, columns = zip(*[(c.name, c.user_defined_values, c) for c in table.columns if c.is_unique])
    names, values, columns = [], [], []
    for c in table.columns:
        if c.is_unique:
            names.append(c.name)
            values.append(c.user_defined_values)
            columns.append(c)

    # Get the total number of rows
    possible_n = total_possible_combinations(table)
    num_rows = int(possible_n) if possible_n <= MAX_ROWS else random_num_rows()
    rows = []

    # If possible_n is not infinite, generate from finite combinations
    # This point will only be hit if all unique columns have user-defined values
    if possible_n != inf:
        # Lazy iterator
        all_combinations_iterator = product(*values)  # type: ignore

        # TODO: since this is a lazy iterator, we value performance over memory
        # However, in the future there may need to be a way to randomly sample
        # from the iterator without exhausting it or exceeding memory limits
        combinations = list(islice(all_combinations_iterator, num_rows))
        rows = [
            {n: format_for_postgres(v, col.post_gres_datatype) for n, v, col in zip(names, combo, columns)}
            for combo in combinations
        ]

    # If there are no user-defined values for at least one unique column,
    # generate random data from combination of unique values arrays and
    # values that can be anything
    else:
        seen_combinations = set()  # Set to track unique combinations
        i = 0
        while len(rows) < num_rows:
            if i >= MAX_ROWS:  # Break if the loop runs too long
                break

            row = {}
            for name, val_list, col in zip(names, values, columns):
                if bool(val_list):  # Pick a random value from the user-defined list (i.e., enums)
                    row[name] = format_for_postgres(choice(val_list), col.post_gres_datatype)  # type: ignore
                elif col.is_foreign_key:  # Pick a random foreign key value
                    row[name] = pick_random_foreign_key(name, table, remember_fn)
                else:  # Generate random data (e.g., a new username)
                    row[name] = generate_fake_data(
                        col.post_gres_datatype, col.nullable(), col.max_length, col.name, col.user_defined_values
                    )
            # Create a tuple of the row items sorted by key to ensure uniqueness is properly checked
            row_tuple = tuple(row[name] for name in sorted(row))
            if row_tuple not in seen_combinations:
                seen_combinations.add(row_tuple)
                rows.append(row)

            # If the combination is not unique, the loop continues without adding the row
            i += 1

    return rows


def generate_seed_data(tables: list[TableInfo]) -> dict[str, list[list[Any]]]:
    """Generate seed data for the tables."""
    seed_data = {}
    memory: dict[str, dict[str, set[Any]]] = {}
    sorted_tables, _ = sort_tables_for_insert(tables)

    def _memorize(table_name: str, column_name: str, data: Any) -> None:
        """Add data to memory."""
        if table_name not in memory:
            memory[table_name] = dict()
        if column_name not in memory[table_name]:
            memory[table_name][column_name] = set()
        memory[table_name][column_name].add(data)

    def _remember(table_name: str, column_name: str) -> set[Any]:  # type: ignore
        """Get data from memory."""
        try:
            return memory[table_name][column_name]
        except KeyError:
            logger.error(f'Could not remember data for {table_name}.{column_name}')

    def _rows_for_datetime_parsing(
        data: list[list[Any]], header: list[Any], columns: list[ColumnInfo]
    ) -> Generator[dict[str, tuple[int, str, Any]], None, None]:
        """Organize the rows for datetime parsing."""

        # Ensure there is at least one row (the header row)
        if not data or len(data) < 2:
            raise ValueError('Data must contain at least one header row and one data row.')

        # Get mapping of column names to postgres data types
        column_types = {c.name: c.post_gres_datatype for c in columns}

        # Iterate over each subsequent row
        for row in data:
            # Create a dictionary for the current row
            row_dict = {}
            for i, (key, value) in enumerate(zip(header, row)):
                # Determine the type of the value
                value_type = column_types[key]  # type(value).__name__
                # Assign the (type, value) tuple to the corresponding key
                row_dict[key] = (i, value_type, value)

            # Yield the dictionary for the current row
            yield row_dict

    for table_name in sorted_tables:
        table = next((t for t in tables if t.name == table_name), None)
        if table is None:
            logger.error(f'Could not find table {table_name}')
            continue

        unique_rows = unique_data_rows(table, _remember)
        fake_data = [[c.name for c in table.columns]]  # Add headers first
        num_rows = len(unique_rows) if unique_rows else random_num_rows()
        # print(unique_rows, num_rows)

        for i in range(int(num_rows)):
            row = []
            for column in table.columns:
                # Use unique values already generated to coordinate data additions
                # correctly.
                if column.is_unique:
                    data = unique_rows[i][column.name]

                # Choose a random foreign key value
                elif column.is_foreign_key:
                    data = pick_random_foreign_key(column.name, table, _remember)

                # Else, generate new value
                else:
                    data = generate_fake_data(
                        column.post_gres_datatype,
                        column.nullable(),
                        column.max_length,
                        column.name,
                        column.user_defined_values,
                    )

                # Add to memory
                if column.primary or column.is_unique or column.is_foreign_key:
                    _memorize(table_name, column.name, data)

                row.append(data)
            fake_data.append(row)

        # Modify fake data for datetime sequences
        headers = fake_data[0]
        fake_data = [
            guess_datetime_order(row) for row in _rows_for_datetime_parsing(fake_data[1:], headers, table.columns)
        ]
        fake_data.insert(0, headers)

        # Add foreign keys
        seed_data[table_name] = fake_data

    return seed_data
