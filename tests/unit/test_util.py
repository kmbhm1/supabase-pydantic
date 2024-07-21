from supabase_pydantic.util.util import get_pydantic_type, get_sqlalchemy_type


def test_all_postgres_data_types_are_mapped_to_pydantic_and_sqlalchemy():
    """Test that all PostgreSQL data types are mapped to Pydantic and SQLAlchemy types."""
    postgres_data_types = [
        'smallint',
        'integer',
        'bigint',
        'decimal',
        'numeric',
        'real',
        'double precision',
        'serial',
        'bigserial',
        'money',
        'character varying(n)',
        'varchar(n)',
        'character(n)',
        'char(n)',
        'text',
        'bytea',
        'timestamp',
        'timestamp with time zone',
        'date',
        'time',
        'time with time zone',
        'interval',
        'boolean',
        'enum',
        'point',
        'line',
        'lseg',
        'box',
        'path',
        'polygon',
        'circle',
        'cidr',
        'inet',
        'macaddr',
        'macaddr8',
        'bit',
        'bit varying',
        'tsvector',
        'tsquery',
        'uuid',
        'xml',
        'json',
        'jsonb',
        'integer[]',
        'any',
        'void',
        'record',
    ]

    for data_type in postgres_data_types:
        assert get_pydantic_type(data_type) is not None
        assert get_sqlalchemy_type(data_type) is not None
