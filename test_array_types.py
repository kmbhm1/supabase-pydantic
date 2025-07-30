from supabase_pydantic.util.util import get_pydantic_type

# Test different array types
array_types = [
    'text[]',
    'integer[]',
    'boolean[]',
    'uuid[]',
    'timestamp[]',
    'MyEnum[]',  # Test with a custom enum type
]

print('Testing array type handling for Pydantic models:')
print('-' * 50)
for t in array_types:
    base_type = t[:-2]  # Remove the [] suffix
    result = get_pydantic_type(t)
    print(f'PostgreSQL type: {t}')
    print(f'  Base type: {base_type}')
    print(f'  Pydantic type: {result[0]}')
    print(f'  Import: {result[1]}')
    print()
