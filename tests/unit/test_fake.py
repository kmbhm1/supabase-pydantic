from datetime import date, datetime, timedelta
from faker import Faker
import pytest
from unittest.mock import patch
from dateutil.parser import parse

from supabase_pydantic.util.fake import (
    generate_fake_data,
    guess_and_generate_fake_data,
    guess_datetime_order,
    random_datetime_within_N_years,
)


@pytest.fixture
def fake_faker():
    """Fixture to mock Faker methods used in generate_fake_data."""
    with patch('supabase_pydantic.util.fake.Faker') as mock_faker:  # Adjust the patch location to where Faker is used
        fake = mock_faker.return_value
        fake.random_number.return_value = 12345
        fake.email.return_value = 'example@example.com'
        fake.text.return_value = 'This is a fake text.'
        fake.boolean.return_value = True
        fake.date.return_value = '2022-01-01'
        fake.date_time.return_value = '2022-01-01 10:00:00'
        fake.uuid4.return_value = '123e4567-e89b-12d3-a456-426614174000'
        fake.profile.return_value = {'name': 'John Doe', 'age': 30}
        yield fake


@pytest.fixture
def mock_random():
    """Fixture to control randomness in the generate_fake_data function."""
    with patch('random.random') as mock_rand:
        mock_rand.return_value = 0.1  # Always above the threshold for nullable
        yield mock_rand


def test_integer_datatype(fake_faker, mock_random):
    """Test that integers are generated correctly."""
    result = generate_fake_data('integer', False, None, 'foo', None, fake_faker)
    assert result == 12345


def test_nullable_field(fake_faker, monkeypatch):
    """Test that nullable fields can return 'NULL'."""
    monkeypatch.setattr('supabase_pydantic.util.fake.random', lambda: 0.01)  # Below the threshold to simulate null
    result = generate_fake_data('text', True, None, 'foo', None, fake_faker)
    assert result == 'NULL'


def test_text_datatype(fake_faker, mock_random):
    """Test text data generation, especially with specific column names like email."""
    email_result = generate_fake_data('text', False, None, 'email', None, fake_faker)
    assert email_result == "'example@example.com'"

    text_result = generate_fake_data('text', False, 20, 'foo', None, fake_faker)
    assert text_result == "'This is a fake text.'"


def test_boolean_datatype(fake_faker, mock_random):
    """Test boolean data generation."""
    result = generate_fake_data('boolean', False, None, 'foo', None, fake_faker)
    assert result is True


def test_date_datatype(fake_faker, mock_random):
    """Test date data generation."""
    result = generate_fake_data('date', False, None, 'foo', None, fake_faker)
    assert result == "'2022-01-01'"


def test_timestamp_datatype(fake_faker, mock_random):
    """Test timestamp data generation."""
    result = generate_fake_data('timestamp', False, None, 'foo', None, fake_faker)
    assert result == "'2022-01-01 10:00:00'"

    # Note, for mocking purposes the timestamps will all be the same
    result = generate_fake_data('timestamp with time zone', False, None, 'foo', None, fake_faker)
    assert result == "'2022-01-01 10:00:00'"
    result = generate_fake_data('timestamp without time zone', False, None, 'foo', None, fake_faker)
    assert result == "'2022-01-01 10:00:00'"


def test_uuid_datatype(fake_faker, mock_random):
    """Test UUID data generation."""
    result = generate_fake_data('uuid', False, None, 'foo', None, fake_faker)
    assert result == "'123e4567-e89b-12d3-a456-426614174000'"


def test_json_datatype(fake_faker, mock_random):
    """Test JSON data type using a custom JSON encoder."""
    json_result = generate_fake_data('json', False, None, 'profile', None, fake_faker)
    expected_json = '"{\\"name\\": \\"John Doe\\", \\"age\\": 30}"'
    assert json_result == f"'{expected_json}'"


def test_unsupported_datatype(fake_faker, mock_random):
    """Test that unsupported data types return 'NULL'."""
    result = generate_fake_data('unsupported', False, None, 'foo', None, fake_faker)
    assert result == 'NULL'


def test_user_defined_datatype(fake_faker):
    """Test user-defined data type."""
    faker = Faker()
    result = generate_fake_data('user-defined', False, None, 'foo', ['bar', 'baz'], faker)
    assert result in ["'bar'", "'baz'"]
    result = generate_fake_data('user-defined', False, None, 'foo', None, faker)
    assert result == 'NULL'


# Test for random_datetime_within_N_years
def test_random_datetime_within_N_years():
    dt = random_datetime_within_N_years(2)
    now = datetime.now()
    max_date = now - timedelta(days=2 * 365)
    end_date = now - timedelta(days=60)
    assert max_date <= dt <= end_date, f'Generated datetime {dt} is not within the expected range.'


def is_datetime_string(date_string: str) -> bool:
    """Check if a string can be parsed as a datetime using dateutil."""
    try:
        parse(date_string)
        return True
    except ValueError:
        return False


def test_guess_datetime_order():
    row = {
        'created_at': (0, 'timestamp', datetime(2023, 8, 1)),
        'updated_at': (1, 'timestamp', datetime(2024, 5, 1)),
        'deleted_at': (2, 'timestamp', datetime(2023, 12, 1)),
        'birthdate': (3, 'date', datetime(1985, 7, 1)),
    }
    ordered_row = guess_datetime_order(row)
    assert len(ordered_row) == len(row)

    check = [parse(item) for item in ordered_row]
    assert check[0] < check[1] < check[2], 'Datetime order is incorrect'


@pytest.mark.parametrize(
    'column_name, expected_type',
    [
        ('username', str),
        ('email', str),
        ('created_at', datetime),
        ('updated_at', datetime),
        ('birthdate', date),
        ('phone_number', str),
    ],
)
def test_guess_and_generate_fake_data(column_name, expected_type):
    result = guess_and_generate_fake_data(column_name)
    assert isinstance(
        result, expected_type
    ), f'Expected {expected_type} but got {type(result)} for column {column_name}'


@pytest.mark.parametrize(
    'column_name, expected_type',
    [
        ('username', str),
        ('email', str),
        ('created_at', datetime),
        ('updated_at', datetime),
        ('birthdate', date),
        ('phone_number', str),
    ],
)
def test_guess_and_generate_fake_data_handles_provided_data_type(column_name, expected_type):
    result = guess_and_generate_fake_data(column_name, data_type='foo')
    assert isinstance(
        result, expected_type
    ), f'Expected {expected_type} but got {type(result)} for column {column_name} with provided date_type'

    result = guess_and_generate_fake_data(column_name, data_type='int')
    assert isinstance(
        result, expected_type
    ), f'Expected {expected_type} but got {type(result)} for column {column_name} with provided date_type'


# Test for generate_fake_data
@pytest.mark.parametrize(
    'data_type, nullable, max_length, name, expected_type',
    [
        ('integer', False, None, 'id', int),
        ('text', False, 100, 'description', str),
        ('date', False, None, 'birthdate', str),
        ('timestamp', False, None, 'created_at', str),
        ('uuid', False, None, 'uuid', str),
        ('json', False, None, 'metadata', str),
    ],
)
def test_generate_fake_data(data_type, nullable, max_length, name, expected_type):
    result = generate_fake_data(data_type, nullable, max_length, name)
    if nullable and result == 'NULL':
        assert True
    else:
        assert isinstance(
            result, expected_type
        ), f'Expected {expected_type} but got {type(result)} for data type {data_type}'
