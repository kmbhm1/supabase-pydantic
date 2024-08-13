import json
from random import random
from typing import Any

from faker import Faker

from supabase_pydantic.util.json import CustomJsonEncoder

faker = Faker()


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

    if datatype in ['integer', 'bigint']:
        return fake.random_number(digits=(max_length if max_length else 5))
    elif datatype == 'text' or 'varchar' in datatype or datatype == 'character varying':
        out = 'NULL'
        if name.lower() == 'email':
            out = fake.email()
        else:
            out = fake.text(max_nb_chars=max_length if max_length else 100).replace("'", r'\'')  # noqa: Q004
        return f"'{out}'"
    elif datatype == 'boolean':
        return fake.boolean()
    elif datatype == 'date':
        return f"'{str(fake.date())}'"
    elif datatype == 'timestamp':
        return f"'{str(fake.date_time())}'"
    elif datatype == 'timestamp with time zone':
        return f"'{str(fake.date_time())}'"
    elif datatype == 'timestamp without time zone':
        return f"'{str(fake.date_time())}'"
    elif datatype == 'uuid':
        return f"'{str(fake.uuid4())}'"
    elif datatype in ['json', 'jsonb']:
        out = json.dumps(fake.profile(), cls=CustomJsonEncoder).replace("'", '')
        return f"'{out}'"  # noqa: Q004
    elif datatype == 'user-defined':
        if user_defined_values:
            return f"'{fake.random_element(user_defined_values)}'"
        else:
            return "'foo'"
    else:
        return 'NULL'
