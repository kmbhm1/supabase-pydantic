import json
import re
from datetime import datetime, timedelta
from random import randint, random
from typing import Any, Literal

from faker import Faker

from src.supabase_pydantic.core.formatters import CustomJsonEncoder

faker = Faker()


def format_for_postgres(value: Any, data_type: str) -> str:
    """Formats a Python value for SQL based on PostgreSQL data type.

    Args:
        value: The Python value to be formatted.
        data_type: The PostgreSQL data type.

    Returns:
        str: The formatted SQL value.
    """
    if value is None:
        return 'NULL'

    # String types in PostgreSQL
    if data_type in ['char', 'varchar', 'text']:
        # Replace single quotes in the string to avoid SQL injection issues
        value = str(value).replace("'", "\\'")
        return f"'{value}'"

    # Numeric types in PostgreSQL
    elif data_type in ['int', 'integer', 'bigint', 'smallint', 'numeric', 'real', 'double precision']:
        return str(value)

    # Boolean type in PostgreSQL
    elif data_type == 'boolean':
        return 'true' if value else 'false'

    # Date and time types in PostgreSQL
    elif data_type in ['date', 'timestamp', 'time']:
        return f"'{value}'"

    # Special types like JSON needs to be converted to a string and escaped
    elif data_type in ['json', 'jsonb']:
        import json

        json_str = json.dumps(value)
        json_str = json_str.replace("'", "''")
        return f"'{json_str}'"

    # If the type is unknown or unsupported
    else:
        return f"'{value}'"


def random_datetime_within_N_years(n: int = 2) -> Any:
    """Generate a random datetime within the last N years."""
    now = datetime.now()
    max_date = now - timedelta(days=n * 365)
    end_date = now - timedelta(days=60)
    return faker.date_time_between(start_date=max_date, end_date=end_date)


def guess_datetime_order(row: dict[str, tuple[int, str, Any]]) -> list[Any]:
    """Guess the ordering of datetimes in a row and return a list of values.

    The definition of the dictionary is column_name: (order in final list, data_type, value).

    Args:
        row (dict): A dictionary of column names and their values.

    Returns:
        list: A list of values ordered by their group and within each group.
    """
    postgres_date_datatypes = ['date', 'timestamp', 'timestamp with time zone', 'timestamp without time zone']

    # Define grouped datetime columns in order of precedence
    datetime_groups = [
        (r'birthdate|dob', 'dob'),
        (r'created_at|created_on|creation_date', 'created'),
        (r'published_at|published_on|publish_date', 'published'),
        (r'modified_at|modified_on|last_modified', 'modified'),
        (r'accessed_at|accessed_on|last_accessed', 'accessed'),
        (r'updated_at|updated_on|last_updated', 'updated'),
        (r'inserted_at|inserted_on', 'inserted'),
        (r'started_at|started_on|start_date', 'started'),
        (r'completed_at|completed_on|completion_date', 'completed'),
        (r'archived_at|archived_on|archived_on', 'archived'),
        (r'timestamp|log_timestamp', 'logging'),
        (r'deleted_at|deleted_on|removal_date', 'deleted'),
        (r'expired_at|expired_on|expiry_date|expire_date', 'expired'),
        (r'hire_date|hired_on|hired_at', 'hired'),
        (r'termination_date|terminated_on|terminated_at', 'termination'),
    ]

    # Start with a base datetime for the sequence of fake timestamps
    base_time = random_datetime_within_N_years(5)
    dob_date = base_time - timedelta(days=365 * randint(18, 40))  # Subtract 18-40 years from the base time

    def _time_step() -> timedelta:
        return timedelta(  # Increment
            days=randint(1, 4),
            hours=randint(0, 23),
            minutes=randint(0, 59),
            seconds=randint(0, 59),
        )

    # Initialize group dict with each column's value and group
    grouped = {}
    output_values = []

    # Prepare list of values to be returned, initialized to None
    for order, (col_name, (col_order, col_type, col_value)) in enumerate(row.items()):
        output_values.append(None)

    # Sort values by their group and add to output list
    for col_name, (col_order, col_type, col_value) in row.items():
        # Check if this column is a datetime column and assign to appropriate group
        if col_type in postgres_date_datatypes:
            # Determine the group by matching the column name against the group patterns
            group = None
            for pattern, group_name in datetime_groups:
                if re.search(pattern, col_name, re.IGNORECASE):
                    group = group_name
                    break

            # If no match found, keep the column in its original place
            if group is None:
                output_values[col_order] = format_for_postgres(col_value, col_type)
                continue

            # Add to group dictionary
            if group not in grouped:
                grouped[group] = []
            grouped[group].append((col_order, col_type, col_value))

    # Process DOB group first if exists
    if 'dob' in grouped:
        for col_order, col_type, _ in grouped['dob']:
            output_values[col_order] = format_for_postgres(dob_date, col_type)

    # Process other groups in order
    current_time = base_time
    for group_name, group_items in grouped.items():
        if group_name == 'dob':
            continue  # Already processed

        for col_order, col_type, _ in group_items:
            output_values[col_order] = format_for_postgres(current_time, col_type)

        # Increment time for next group
        current_time += _time_step()

    return output_values


def guess_and_generate_fake_data(
    column_name: str, faker: Faker = faker, data_type: Literal['int', 'float', 'bool', 'str'] | None = None
) -> Any:
    """Guess the data type based on the column name and generate fake data."""
    # Define patterns for different data types and the corresponding faker method
    patterns = {
        'id': (r'^id$|_id$', lambda: faker.random_number(digits=5)),
        'name': (r'name', faker.name),
        'first_name': (r'first.*name', faker.first_name),
        'last_name': (r'last.*name', faker.last_name),
        'username': (r'username', faker.user_name),
        'email': (r'email', faker.email),
        'address': (r'address', faker.address),
        'street': (r'street', faker.street_address),
        'city': (r'city', faker.city),
        'state': (r'state', faker.state),
        'zipcode': (r'zipcode|postal_code', faker.zipcode),
        'country': (r'country', faker.country),
        'phone': (r'phone', faker.phone_number),
        'company': (r'company', faker.company),
        'job': (r'job|profession|occupation', faker.job),
        'description': (r'description|summary|detail', faker.text),
        'title': (r'title', faker.sentence),
        'content': (r'content|body', faker.paragraph),
        'created_at': (r'created_at', faker.date_time),
        'updated_at': (r'updated_at', faker.date_time),
        'birthdate': (r'birthdate|dob|birth_date', faker.date_of_birth),
        'password': (r'password', faker.password),
        'website': (r'website', faker.url),
        'ip_address': (r'ip.*address', faker.ipv4),
        'domain_name': (r'domain.*name', faker.domain_name),
        'url': (r'url', faker.url),
        'image_url': (r'image.*url', faker.image_url),
        'mac_address': (r'mac.*address', faker.mac_address),
        'uuid': (r'uuid', faker.uuid4),
        'slug': (r'slug', faker.slug),
        'credit_card_number': (r'credit.*card.*number', faker.credit_card_number),
        'credit_card_expire': (r'credit.*card.*expire', faker.credit_card_expire),
        'credit_card_provider': (r'credit.*card.*provider', faker.credit_card_provider),
        'iban': (r'iban', faker.iban),
        'currency_code': (r'currency.*code', faker.currency_code),
        'color': (r'color', faker.color_name),
        'license_plate': (r'license.*plate', faker.license_plate),
        'file_name': (r'file.*name', faker.file_name),
        'mime_type': (r'mime.*type', faker.mime_type),
        'time': (r'time', faker.time),
        'month': (r'month', faker.month_name),
        'year': (r'year', faker.year),
    }

    # Search for a matching pattern and generate data
    for _, (pattern, func) in patterns.items():
        if re.search(pattern, column_name, re.IGNORECASE):
            data = func()
            if data_type:
                try:
                    # Convert data to the specified type
                    if data_type == 'int':
                        return int(data)
                    elif data_type == 'float':
                        return float(data)
                    elif data_type == 'bool':
                        return bool(data)
                    elif data_type == 'str':
                        return str(data)
                except ValueError as e:
                    print(f'Error converting data_type "{data_type}" with data "{data}"')
                    print(f'Error: {e}')
                    return data  # Return original data if conversion fails
            return data

    return None  # Return None if no matching pattern found


def generate_fake_data(
    post_gres_datatype: str,
    is_nullable: bool,
    max_length: int | None,
    name: str,
    user_defined_values: list[str] | None = None,
    fake: Faker = faker,
) -> Any:
    """Generate fake data based on the column datatype."""
    datatype = post_gres_datatype.lower()

    # If user-defined values are provided, use them regardless of data type
    if user_defined_values:
        return user_defined_values[0]

    if is_nullable and random() < 0.15:
        return 'NULL'

    data_base_on_name = guess_and_generate_fake_data(name, fake)
    if data_base_on_name:
        return format_for_postgres(data_base_on_name, post_gres_datatype)

    if datatype in ['integer', 'bigint']:
        return fake.random_number(digits=(max_length if max_length else 5))
    elif datatype == 'text' or 'varchar' in datatype or datatype == 'character varying':
        out = fake.text(max_nb_chars=max_length if max_length else 100).replace("'", r'\'')  # noqa: Q004
        return format_for_postgres(out, post_gres_datatype)
    elif datatype == 'boolean':
        return fake.boolean()
    elif datatype == 'date':
        return format_for_postgres(fake.date(), post_gres_datatype)
    elif datatype == 'timestamp':
        return format_for_postgres(fake.date_time(), post_gres_datatype)
    elif datatype == 'timestamp with time zone':
        return format_for_postgres(fake.date_time(), post_gres_datatype)
    elif datatype == 'timestamp without time zone':
        return format_for_postgres(fake.date_time(), post_gres_datatype)
    elif datatype == 'uuid':
        return format_for_postgres(fake.uuid4(), post_gres_datatype)
    elif datatype in ['json', 'jsonb']:
        out = json.dumps(fake.profile(), cls=CustomJsonEncoder).replace("'", '')
        return format_for_postgres(out, post_gres_datatype)  # noqa: Q004
    elif datatype == 'user-defined':
        if user_defined_values:
            return format_for_postgres(fake.random_element(user_defined_values), post_gres_datatype)
        else:
            return 'NULL'
    else:
        return 'NULL'
