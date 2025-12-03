import pytest

from supabase_pydantic.db.drivers.mysql.constants import (
    MYSQL_CONSTRAINT_TYPE_MAP,
    MYSQL_USER_DEFINED_TYPE_MAP,
)


@pytest.mark.unit
@pytest.mark.constants
def test_mysql_constraint_type_map_contents() -> None:
    assert MYSQL_CONSTRAINT_TYPE_MAP['PRIMARY KEY'] == 'PRIMARY KEY'
    assert MYSQL_CONSTRAINT_TYPE_MAP['FOREIGN KEY'] == 'FOREIGN KEY'
    assert MYSQL_CONSTRAINT_TYPE_MAP['UNIQUE'] == 'UNIQUE'
    assert MYSQL_CONSTRAINT_TYPE_MAP['CHECK'] == 'CHECK'

    # Ensure there are no unexpected keys
    assert set(MYSQL_CONSTRAINT_TYPE_MAP.keys()) == {'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'CHECK'}


@pytest.mark.unit
@pytest.mark.constants
def test_mysql_user_defined_type_map_contents() -> None:
    assert MYSQL_USER_DEFINED_TYPE_MAP == {'ENUM': 'ENUM', 'SET': 'SET'}
