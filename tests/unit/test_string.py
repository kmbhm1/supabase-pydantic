from supabase_pydantic.util.util import to_pascal_case


def test_to_pascal_case():
    """Test to_pascal_case."""
    assert to_pascal_case('snake_case') == 'SnakeCase'
    assert to_pascal_case('snake_case_with_more_words') == 'SnakeCaseWithMoreWords'
    assert to_pascal_case('snake') == 'Snake'
    assert to_pascal_case('snake_case_with_1_number') == 'SnakeCaseWith1Number'
    assert to_pascal_case('snake_case_with_1_number_and_1_symbol!') == 'SnakeCaseWith1NumberAnd1Symbol!'
