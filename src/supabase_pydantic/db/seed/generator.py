"""Seed data generation utilities for database tables."""

import pprint
from collections.abc import Callable, Generator
from random import choice, randint
from typing import Any

from src.supabase_pydantic.db.graph import sort_tables_for_insert
from src.supabase_pydantic.db.models import ColumnInfo, TableInfo
from src.supabase_pydantic.db.seed.fake import generate_fake_data, guess_datetime_order

pp = pprint.PrettyPrinter(indent=4)
MAX_ROWS = 200


def total_possible_combinations(table: TableInfo) -> int:
    """Get the number of maximum rows for a table based on the unique rows."""
    # Find all columns that need unique values
    unique_cols = [c for c in table.columns if c.is_unique or c.primary]

    # If there are no unique columns, return a large number
    if not unique_cols:
        return 1_000_000  # Use a large integer instead of infinity

    # Calculate total possible combinations based on unique constraints
    possible_combinations = 1
    for col in unique_cols:
        post_gres_type = col.post_gres_datatype.lower()
        if post_gres_type == 'boolean':
            possible_combinations *= 2
        elif col.max_length is not None:
            possible_combinations *= 10 ** min(col.max_length, 5)  # Max 5 digits for numeric types
        else:
            possible_combinations *= 100  # Arbitrary large number for other types

    return min(possible_combinations, MAX_ROWS)


def random_num_rows() -> int:
    """Generate a random number of rows."""
    return randint(10, 30)


def pick_random_foreign_key(column_name: str, table: TableInfo, remember_fn: Callable) -> Any:
    """Pick a random foreign key value for a column."""
    # Find the foreign key constraint for this column
    foreign_key_info = next(
        (fk for fk in table.foreign_keys if fk.column_name == column_name),
        None,
    )

    if foreign_key_info is None:
        print(f'Could not find foreign key for column {column_name}')
        return 'NULL'

    # Get the data from memory
    foreign_values = remember_fn(foreign_key_info.foreign_table_name, foreign_key_info.foreign_column_name)
    if not foreign_values:
        print(
            f'No data found for {foreign_key_info.foreign_table_name}.{foreign_key_info.foreign_column_name}.',
        )
        # Return a default value if we couldn't find the data
        return 'NULL'

    # Pick a random value from the set
    return choice(list(foreign_values))


def unique_data_rows(table: TableInfo, remember_fn: Callable) -> list[dict[str, Any]]:
    """Generate unique data rows for a table based on the unique columns."""
    # Find all columns that need unique values
    unique_cols = [c for c in table.columns if c.is_unique or c.primary]

    # If there are no columns with unique constraints, return an empty list
    if not unique_cols:
        return []

    # Calculate the max number of rows we can generate
    max_rows = int(min(total_possible_combinations(table), MAX_ROWS))

    # List for storing rows
    rows: list[dict[str, Any]] = []

    # Set for tracking seen combinations
    seen_combinations = set()

    # Counter for tracking number of iterations
    i = 0
    max_attempts = max_rows * 10  # Try up to 10 times max_rows attempts

    # Keep generating rows until we have enough
    while len(rows) < max_rows and i < max_attempts:
        row = {}

        # For each unique column, generate data
        for col in unique_cols:
            # If it's a foreign key, pick a random value from the related table
            if col.is_foreign_key:
                data = pick_random_foreign_key(col.name, table, remember_fn)
            # Otherwise generate new data
            else:
                data = generate_fake_data(
                    col.post_gres_datatype,
                    col.nullable(),
                    col.max_length,
                    col.name,
                    col.user_defined_values,
                )

            row[col.name] = data

        # Check if this combination of values has been seen before
        row_tuple = tuple(row.items())
        if row_tuple not in seen_combinations:
            seen_combinations.add(row_tuple)
            rows.append(row)

        # If the combination is not unique, the loop continues without adding the row
        i += 1

    return rows


def write_seed_file(seed_data: dict[str, list[list[Any]]], output_file: str, overwrite: bool = False) -> list[str]:
    """Write the seed data to a SQL file.

    Args:
        seed_data: The seed data to write.
        output_file: The path to the output file.
        overwrite: Whether to overwrite existing files.
    
    Returns:
        List of file paths that were written.
    """
    with open(output_file, 'w') as f:
        # Write file header
        f.write('-- Auto-generated seed data\n')
        f.write('-- DO NOT EDIT DIRECTLY\n\n')

        # Process each table's data
        for table_name, data in seed_data.items():
            if len(data) <= 1:  # Skip if only headers or empty
                continue

            # Write table header
            f.write(f'-- {table_name} data\n')

            # Extract column names from the first row (header)
            columns = data[0]
            column_list = ', '.join(columns)

            # Start the insert statement
            f.write(f'INSERT INTO {table_name} ({column_list})\nVALUES\n')

            # Write each row of data
            value_rows = []
            for row in data[1:]:  # Skip header row
                formatted_values = []
                for val in row:
                    if val is None or val == 'NULL':
                        formatted_values.append('NULL')
                    elif isinstance(val, str):
                        # Escape single quotes for SQL
                        escaped_val = val.replace("'", "''")
                        formatted_values.append(f"'{escaped_val}'")
                    else:
                        formatted_values.append(str(val))

                value_row = '(' + ', '.join(formatted_values) + ')'
                value_rows.append(value_row)

            # Join all rows with commas and end with semicolon
            f.write(',\n'.join(value_rows))
            f.write(';\n\n')

        # End the file with a comment
        f.write('-- End of seed data\n')
        
    return [output_file]  # Return the file path that was written


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
            print(f'Could not remember data for {table_name}.{column_name}')

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
            print(f'Could not find table {table_name}')
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
