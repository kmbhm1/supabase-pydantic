import pytest
from unittest.mock import patch
import json

from supabase_pydantic.util.fake import generate_fake_data


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
    result = generate_fake_data('integer', False, None, 'foo', fake_faker)
    assert result == 12345


def test_nullable_field(fake_faker, monkeypatch):
    """Test that nullable fields can return 'NULL'."""
    monkeypatch.setattr('supabase_pydantic.util.fake.random', lambda: 0.01)  # Below the threshold to simulate null
    result = generate_fake_data('text', True, None, 'foo', fake_faker)
    assert result == 'NULL'


def test_text_datatype(fake_faker, mock_random):
    """Test text data generation, especially with specific column names like email."""
    email_result = generate_fake_data('text', False, None, 'email', fake_faker)
    assert email_result == "'example@example.com'"

    text_result = generate_fake_data('text', False, 20, 'foo', fake_faker)
    assert text_result == "'This is a fake text.'"


def test_boolean_datatype(fake_faker, mock_random):
    """Test boolean data generation."""
    result = generate_fake_data('boolean', False, None, 'foo', fake_faker)
    assert result is True


def test_date_datatype(fake_faker, mock_random):
    """Test date data generation."""
    result = generate_fake_data('date', False, None, 'foo', fake_faker)
    assert result == "'2022-01-01'"


def test_timestamp_datatype(fake_faker, mock_random):
    """Test timestamp data generation."""
    result = generate_fake_data('timestamp', False, None, 'foo', fake_faker)
    assert result == "'2022-01-01 10:00:00'"

    # Note, for mocking purposes the timestamps will all be the same
    result = generate_fake_data('timestamp with time zone', False, None, 'foo', fake_faker)
    assert result == "'2022-01-01 10:00:00'"
    result = generate_fake_data('timestamp without time zone', False, None, 'foo', fake_faker)
    assert result == "'2022-01-01 10:00:00'"


def test_uuid_datatype(fake_faker, mock_random):
    """Test UUID data generation."""
    result = generate_fake_data('uuid', False, None, 'foo', fake_faker)
    assert result == "'123e4567-e89b-12d3-a456-426614174000'"


def test_json_datatype(fake_faker, mock_random):
    """Test JSON data type using a custom JSON encoder."""
    json_result = generate_fake_data('json', False, None, 'profile', fake_faker)
    expected_json = json.dumps(
        {'name': 'John Doe', 'age': 30}, cls=json.JSONEncoder
    )  # Assuming you import JSONEncoder or use CustomJsonEncoder correctly in your environment
    assert json_result == f"'{expected_json}'"


def test_unsupported_datatype(fake_faker, mock_random):
    """Test that unsupported data types return 'NULL'."""
    result = generate_fake_data('unsupported', False, None, 'foo', fake_faker)
    assert result == 'NULL'
