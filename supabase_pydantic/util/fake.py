import json
import re
from random import random
from typing import Any, Literal

from faker import Faker

from supabase_pydantic.util.json import CustomJsonEncoder

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

    # Array types (assuming the array elements are of string type for simplicity)
    # elif '[]' in data_type:  # Simplistic check for an array type
    #     array_content = ", ".join(format_for_postgres(elem, data_type.replace('[]', '')) for elem in value)
    #     return f"ARRAY[{array_content}]"

    # If the type is unknown or unsupported
    else:
        return f"'{value}'"
        # raise ValueError(f'Unsupported data type: {data_type}')


def guess_and_generate_fake_data(
    column_name: str, faker: Faker = faker, data_type: Literal['int', 'float', 'bool', 'str'] | None = None
) -> Any:
    """Guess the data type based on the column name and generate fake data."""

    # Dictionary mapping data items to their regex patterns and Faker methods
    patterns = {
        'username': (r'username', faker.user_name),
        'email': (r'email', faker.email),
        'password': (r'password', faker.password),
        'phone_number': (r'phone.*number', faker.phone_number),
        'phone_extension': (r'phone.*extension', lambda: faker.numerify(text='###')),
        'first_name': (r'first.*name', faker.first_name),
        'last_name': (r'last.*name', faker.last_name),
        'full_name': (r'(full.*name|name)', faker.name),
        # 'name': (r'^name$', faker.name),
        'address': (r'address', faker.address),
        'address_1': (r'address.*1', faker.address),
        'street_name': (r'street.*name', faker.street_name),
        'street_address': (r'street.*address', faker.street_address),
        'secondary_address': (r'secondary.*address', faker.secondary_address),
        'address_2': (r'address.*2', faker.secondary_address),
        'city': (r'city', faker.city),
        'state': (r'state', faker.state),
        'country': (r'country', faker.country),
        'zip_code': (r'zip.*code', faker.zipcode),
        'zip': (r'^zip$', faker.zipcode),
        'postcode': (r'post.*code', faker.postcode),
        'latitude': (r'latitude', lambda: str(faker.latitude())),
        'longitude': (r'longitude', lambda: str(faker.longitude())),
        'ip_address': (r'ip.*address', faker.ipv4),
        'user_agent': (r'user.*agent', faker.user_agent),
        'user_id': (r'user.*id', faker.uuid4),
        'created_at': (r'created.*at', faker.date_time),
        'updated_at': (r'updated.*at', faker.date_time),
        'deleted_at': (r'deleted.*at', faker.date_time),
        'is_': (r'^is_.*', lambda: faker.boolean(chance_of_getting_true=50)),
        'company_name': (r'company.*name', faker.company),
        'company_suffix': (r'company.*suffix', faker.company_suffix),
        'job_title': (r'job.*title', faker.job),
        'ssn': (r'ssn', faker.ssn),
        'birthdate': (r'birth.*date', faker.date_of_birth),
        'age': (r'^age$', lambda: faker.random_int(min=18, max=100)),
        'gender': (r'gender', lambda: faker.random_element(elements=('Male', 'Female'))),
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
        'date_time_this_century': (r'date.*time.*century', faker.date_time_this_century),
    }

    # Search for a matching pattern and generate data
    for _, (pattern, func) in patterns.items():
        if re.search(pattern, column_name, re.IGNORECASE):
            if column_name == 'message':
                print(column_name, pattern, func)
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
                except ValueError:
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

    if is_nullable and random() < 0.15:
        return 'NULL'

    data_base_on_name = guess_and_generate_fake_data(name, fake)
    if data_base_on_name and not bool(user_defined_values):
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
