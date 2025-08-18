"""Tests for column marshaler functions in supabase_pydantic.db.marshalers.column."""

import pytest

from supabase_pydantic.db.marshalers.column import (
    column_name_is_reserved,
    column_name_reserved_exceptions,
    get_alias,
    standardize_column_name,
    string_is_reserved,
)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'value, expected',
    [
        ('int', True),  # Python built-in
        ('print', True),  # Python built-in
        ('for', True),  # Python keyword
        ('def', True),  # Python keyword
        ('username', False),  # Not reserved
        ('customfield', False),  # Not reserved
        ('id', True),  # Built-in
    ],
)
def test_string_is_reserved(value, expected):
    assert string_is_reserved(value) == expected, f'Failed for {value}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', True),
        ('print', True),
        ('model_abc', True),
        ('username', False),
        ('id', True),  # Though 'id' is a built-in, check if it's treated as an exception in another test
    ],
)
def test_column_name_is_reserved(column_name, expected):
    assert column_name_is_reserved(column_name) == expected, f'Failed for {column_name}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected', [('id', True), ('ID', True), ('Id', True), ('username', False), ('int', False)]
)
def test_column_name_reserved_exceptions(column_name, expected):
    assert column_name_reserved_exceptions(column_name) == expected, f'Failed for {column_name}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'field_int'),  # Reserved keyword
        ('print', 'field_print'),  # Built-in name
        ('model_abc', 'field_model_abc'),  # Starts with 'model_'
        ('username', 'username'),  # Not a reserved name
        ('id', 'id'),  # Exception, should not be modified
        ('credits', 'credits'),  # Business term exception, should not be modified
        ('copyright', 'copyright'),  # Business term exception, should not be modified
        ('license', 'license'),  # Business term exception, should not be modified
        ('help', 'help'),  # Business term exception, should not be modified
        ('property', 'property'),  # Business term exception, should not be modified
        ('sum', 'sum'),  # Business term exception, should not be modified
    ],
)
def test_standardize_column_name(column_name, expected):
    assert standardize_column_name(column_name) == expected, f'Failed for {column_name}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'int'),  # Reserved keyword not an exception
        ('model_name', 'model_name'),  # Starts with 'model_'
        ('id', None),  # Exception to reserved keywords
        ('username', None),  # Not a reserved name
    ],
)
def test_get_alias(column_name, expected):
    assert get_alias(column_name) == expected, f'Failed for {column_name}'
