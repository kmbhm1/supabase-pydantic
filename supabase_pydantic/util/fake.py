import json
from random import random
from faker import Faker

from supabase_pydantic.util.json import CustomJsonEncoder


def generate_fake_data(
    post_gres_datatype: str, is_nullable: bool, max_length: int | None, name: str, fake: Faker = Faker()
):
    """Generate fake data based on the column datatype."""
    datatype = post_gres_datatype.lower()

    if is_nullable and random() < 0.15:
        return 'NULL'

    if datatype in ['integer', 'bigint']:
        return fake.random_number(digits=max_length if max_length else 5)
    elif datatype == 'text' or 'varchar' in datatype or datatype == 'character varying':
        if name.lower() == 'email':
            return f"'{fake.email()}'"
        return f"'{fake.text(max_nb_chars=max_length if max_length else 20)}'"
    elif datatype == 'boolean':
        return fake.boolean()
    elif datatype == 'date':
        return f"'{fake.date()}'"
    elif datatype == 'timestamp':
        return f"'{fake.date_time()}'"
    elif datatype == 'timestamp with time zone':
        return f"'{fake.date_time()}'"
    elif datatype == 'timestamp without time zone':
        return f"'{fake.date_time()}'"
    elif datatype == 'uuid':
        return f"'{fake.uuid4()}'"
    elif datatype in ['json', 'jsonb']:
        return f"'{json.dumps(fake.profile(), cls=CustomJsonEncoder)}'"
    else:
        return 'NULL'
