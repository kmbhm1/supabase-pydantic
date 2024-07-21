import decimal
import json
from datetime import datetime, date
import pytest
from supabase_pydantic.util.json import (
    CustomJsonEncoder,
)


def test_encode_decimal():
    """Test encoding of decimal.Decimal."""
    value = decimal.Decimal('10.5')
    expected = '"10.5"'  # JSON representation should be a string of the decimal value
    result = json.dumps(value, cls=CustomJsonEncoder)
    assert result == expected, 'Decimal should be serialized to a JSON string.'


def test_encode_datetime():
    """Test encoding of datetime.datetime."""
    dt = datetime(2022, 7, 20, 15, 30, 45)
    expected = '"2022-07-20T15:30:45"'  # ISO format for datetime
    result = json.dumps(dt, cls=CustomJsonEncoder)
    assert result == expected, 'Datetime should be serialized to ISO 8601 string.'


def test_encode_date():
    """Test encoding of datetime.date."""
    d = date(2022, 7, 20)
    expected = '"2022-07-20"'  # ISO format for date
    result = json.dumps(d, cls=CustomJsonEncoder)
    assert result == expected, 'Date should be serialized to ISO 8601 string.'


def test_encode_complex_object():
    """Test encoding of complex object with mixed types."""
    obj = {
        'decimal': decimal.Decimal('12.34'),
        'datetime': datetime(2023, 1, 1, 12, 0),
        'date': date(2023, 1, 1),
        'string': 'hello',
        'integer': 42,
    }
    expected = '{"decimal": "12.34", "datetime": "2023-01-01T12:00:00", "date": "2023-01-01", "string": "hello", "integer": 42}'
    result = json.dumps(obj, cls=CustomJsonEncoder)
    assert result == expected, 'Complex object should be serialized correctly with custom handling for specified types.'
