"""Tests for string utilities in supabase_pydantic.utils.strings."""

import pytest  # noqa: F401

from supabase_pydantic.utils.strings import (
    chunk_text,
    to_pascal_case,
)


@pytest.mark.unit
@pytest.mark.strings
def test_to_pascal_case():
    """Test to_pascal_case."""
    assert to_pascal_case('snake_case') == 'SnakeCase'
    assert to_pascal_case('snake_case_with_more_words') == 'SnakeCaseWithMoreWords'
    assert to_pascal_case('snake') == 'Snake'
    assert to_pascal_case('snake_case_with_1_number') == 'SnakeCaseWith1Number'
    assert to_pascal_case('snake_case_with_1_number_and_1_symbol!') == 'SnakeCaseWith1NumberAnd1Symbol!'


@pytest.mark.unit
@pytest.mark.strings
def test_chunk_text():
    """Test chunk_text."""
    text = 'This is a test text that will be split into lines with a maximum number of characters.'
    lines = chunk_text(text, nchars=40)
    assert lines == [
        'This is a test text that will be split',
        'into lines with a maximum number of',
        'characters.',
    ]
