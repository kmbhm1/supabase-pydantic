"""Integration tests for the --singular-names CLI functionality.

These tests verify the end-to-end behavior of the singular names feature,
including actual code generation and file output.
"""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
from click.testing import CliRunner

from supabase_pydantic.cli.commands.gen import gen
from supabase_pydantic.db.models import TableInfo, ColumnInfo
from supabase_pydantic.db.database_type import DatabaseType


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_database_setup():
    """Mock database connection and table construction for integration tests."""
    # Create mock table data that represents a typical database schema
    mock_tables = {
        'public': [
            TableInfo(
                name='users',
                schema='public',
                table_type='BASE TABLE',
                columns=[
                    ColumnInfo(
                        name='id', post_gres_datatype='integer', datatype='int', is_nullable=False, primary=True
                    ),
                    ColumnInfo(name='email', post_gres_datatype='character varying', datatype='str', is_nullable=False),
                    ColumnInfo(name='name', post_gres_datatype='character varying', datatype='str', is_nullable=False),
                    ColumnInfo(
                        name='created_at',
                        post_gres_datatype='timestamp with time zone',
                        datatype='datetime',
                        is_nullable=False,
                    ),
                ],
                foreign_keys=[],
                constraints=[],
                relationships=[],
            ),
            TableInfo(
                name='products',
                schema='public',
                table_type='BASE TABLE',
                columns=[
                    ColumnInfo(
                        name='id', post_gres_datatype='integer', datatype='int', is_nullable=False, primary=True
                    ),
                    ColumnInfo(name='name', post_gres_datatype='character varying', datatype='str', is_nullable=False),
                    ColumnInfo(name='price', post_gres_datatype='numeric', datatype='Decimal', is_nullable=False),
                    ColumnInfo(name='category_id', post_gres_datatype='integer', datatype='int', is_nullable=True),
                ],
                foreign_keys=[],
                constraints=[],
                relationships=[],
            ),
            TableInfo(
                name='categories',
                schema='public',
                table_type='BASE TABLE',
                columns=[
                    ColumnInfo(
                        name='id', post_gres_datatype='integer', datatype='int', is_nullable=False, primary=True
                    ),
                    ColumnInfo(name='name', post_gres_datatype='character varying', datatype='str', is_nullable=False),
                    ColumnInfo(name='description', post_gres_datatype='text', datatype='str', is_nullable=True),
                ],
                foreign_keys=[],
                constraints=[],
                relationships=[],
            ),
        ]
    }

    with (
        patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup,
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
    ):
        # Create a proper mock connection params object
        mock_connection_params = Mock()
        mock_connection_params.to_dict.return_value = {'db_url': 'postgresql://test:test@localhost/test'}

        # Mock connection setup
        mock_setup.return_value = (mock_connection_params, DatabaseType.POSTGRES)

        # Mock table construction
        mock_construct.return_value = mock_tables

        yield mock_tables


@pytest.fixture
def runner():
    """Create a CliRunner instance."""
    return CliRunner()


def find_generated_model_file(temp_dir):
    """Helper function to find the generated model file."""
    temp_path = Path(temp_dir)
    # Look for Python files in subdirectories (like fastapi/)
    py_files = list(temp_path.rglob('*.py'))
    if py_files:
        return py_files[0]  # Return the first Python file found
    return None


@pytest.mark.integration
def test_singular_names_end_to_end_pydantic(runner, temp_output_dir, mock_database_setup):
    """Test complete end-to-end generation with --singular-names for Pydantic models."""
    # Run the command with --singular-names
    result = runner.invoke(
        gen,
        [
            '--db-url',
            'postgresql://test:test@localhost/test',
            '--dir',
            temp_output_dir,
            '--type',
            'pydantic',
            '--framework',
            'fastapi',
            '--singular-names',
        ],
    )

    # Command should succeed
    assert result.exit_code == 0, f'Command failed with output: {result.output}'

    # Debug: List all files in the temp directory
    temp_path = Path(temp_output_dir)
    all_files = list(temp_path.rglob('*'))
    print(f'Files created in {temp_output_dir}: {[str(f) for f in all_files]}')

    # Check that files were generated
    model_file = Path(temp_output_dir) / 'model.py'
    if not model_file.exists():
        # Try to find any Python files
        py_files = list(temp_path.rglob('*.py'))
        print(f'Python files found: {[str(f) for f in py_files]}')
        if py_files:
            model_file = py_files[0]  # Use the first Python file found
            print(f'Using file: {model_file}')

    assert model_file.exists(), f'Model file was not generated. Files in directory: {[str(f) for f in all_files]}'

    # Read the generated content
    content = model_file.read_text()

    # Verify singular class names are generated
    assert 'class UserBaseSchema(' in content, 'UserBaseSchema not found (should be singular)'
    assert 'class User(' in content, 'User class not found (should be singular)'
    assert 'class ProductBaseSchema(' in content, 'ProductBaseSchema not found (should be singular)'
    assert 'class Product(' in content, 'Product class not found (should be singular)'
    assert 'class CategoryBaseSchema(' in content, 'CategoryBaseSchema not found (should be singular)'
    assert 'class Category(' in content, 'Category class not found (should be singular)'

    # Verify plural class names are NOT generated
    assert 'class UsersBaseSchema(' not in content, 'UsersBaseSchema found (should be singular)'
    assert 'class Users(' not in content, 'Users class found (should be singular)'
    assert 'class ProductsBaseSchema(' not in content, 'ProductsBaseSchema found (should be singular)'
    assert 'class Products(' not in content, 'Products class found (should be singular)'
    assert 'class CategoriesBaseSchema(' not in content, 'CategoriesBaseSchema found (should be singular)'
    assert 'class Categories(' not in content, 'Categories class found (should be singular)'

    # Verify CRUD models are also singular
    assert 'class UserInsert(' in content, 'UserInsert not found (should be singular)'
    assert 'class UserUpdate(' in content, 'UserUpdate not found (should be singular)'
    assert 'class ProductInsert(' in content, 'ProductInsert not found (should be singular)'
    assert 'class ProductUpdate(' in content, 'ProductUpdate not found (should be singular)'


@pytest.mark.integration
def test_singular_names_end_to_end_sqlalchemy(runner, temp_output_dir, mock_database_setup):
    """Test complete end-to-end generation with --singular-names for SQLAlchemy models."""
    # Run the command with --singular-names for SQLAlchemy
    result = runner.invoke(
        gen,
        [
            '--db-url',
            'postgresql://test:test@localhost/test',
            '--dir',
            temp_output_dir,
            '--type',
            'sqlalchemy',
            '--framework',
            'fastapi',
            '--singular-names',
        ],
    )

    # Command should succeed
    assert result.exit_code == 0, f'Command failed with output: {result.output}'

    # Check that files were generated
    model_file = find_generated_model_file(temp_output_dir)
    assert model_file is not None, 'Model file was not generated'
    assert model_file.exists(), 'Model file was not generated'

    # Read the generated content
    content = model_file.read_text()

    # Verify singular class names are generated for SQLAlchemy
    assert 'class User(' in content, 'User class not found (should be singular)'
    assert 'class Product(' in content, 'Product class not found (should be singular)'
    assert 'class Category(' in content, 'Category class not found (should be singular)'

    # Verify plural class names are NOT generated
    assert 'class Users(' not in content, 'Users class found (should be singular)'
    assert 'class Products(' not in content, 'Products class found (should be singular)'
    assert 'class Categories(' not in content, 'Categories class found (should be singular)'

    # Verify table references are still correct (should reference actual table names)
    assert '# Class for table: users' in content, 'Table reference should still be plural'
    assert '# Class for table: products' in content, 'Table reference should still be plural'
    assert '# Class for table: categories' in content, 'Table reference should still be plural'


@pytest.mark.integration
def test_default_behavior_without_singular_names(runner, temp_output_dir, mock_database_setup):
    """Test that default behavior (without --singular-names) still generates plural class names."""
    # Run the command WITHOUT --singular-names
    result = runner.invoke(
        gen,
        [
            '--db-url',
            'postgresql://test:test@localhost/test',
            '--dir',
            temp_output_dir,
            '--type',
            'pydantic',
            '--framework',
            'fastapi',
        ],
    )

    # Command should succeed
    assert result.exit_code == 0, f'Command failed with output: {result.output}'

    # Check that files were generated
    model_file = find_generated_model_file(temp_output_dir)
    assert model_file is not None, 'Model file was not generated'
    assert model_file.exists(), 'Model file was not generated'

    # Read the generated content
    content = model_file.read_text()

    # Verify plural class names are generated (default behavior)
    assert 'class UsersBaseSchema(' in content, 'UsersBaseSchema not found (should be plural by default)'
    assert 'class Users(' in content, 'Users class not found (should be plural by default)'
    assert 'class ProductsBaseSchema(' in content, 'ProductsBaseSchema not found (should be plural by default)'
    assert 'class Products(' in content, 'Products class not found (should be plural by default)'
    assert 'class CategoriesBaseSchema(' in content, 'CategoriesBaseSchema not found (should be plural by default)'
    assert 'class Categories(' in content, 'Categories class not found (should be plural by default)'

    # Verify singular class names are NOT generated
    assert 'class UserBaseSchema(' not in content, 'UserBaseSchema found (should be plural by default)'
    assert 'class User(' not in content, 'User class found (should be plural by default)'
    assert 'class ProductBaseSchema(' not in content, 'ProductBaseSchema found (should be plural by default)'
    assert 'class Product(' not in content, 'Product class found (should be plural by default)'


@pytest.mark.integration
def test_singular_names_with_complex_table_names(runner, temp_output_dir):
    """Test singular names with complex table names (underscores, compound words)."""
    # Create mock tables with complex names
    complex_tables = {
        'public': [
            TableInfo(
                name='user_profiles',
                schema='public',
                table_type='BASE TABLE',
                columns=[
                    ColumnInfo(
                        name='id', post_gres_datatype='integer', datatype='int', is_nullable=False, primary=True
                    ),
                    ColumnInfo(name='user_id', post_gres_datatype='integer', datatype='int', is_nullable=False),
                    ColumnInfo(name='bio', post_gres_datatype='text', datatype='str', is_nullable=True),
                ],
                foreign_keys=[],
                constraints=[],
                relationships=[],
            ),
            TableInfo(
                name='order_items',
                schema='public',
                table_type='BASE TABLE',
                columns=[
                    ColumnInfo(
                        name='id', post_gres_datatype='integer', datatype='int', is_nullable=False, primary=True
                    ),
                    ColumnInfo(name='order_id', post_gres_datatype='integer', datatype='int', is_nullable=False),
                    ColumnInfo(name='product_id', post_gres_datatype='integer', datatype='int', is_nullable=False),
                    ColumnInfo(name='quantity', post_gres_datatype='integer', datatype='int', is_nullable=False),
                ],
                foreign_keys=[],
                constraints=[],
                relationships=[],
            ),
        ]
    }

    with (
        patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup,
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
    ):
        # Create a proper mock connection params object
        mock_connection_params = Mock()
        mock_connection_params.to_dict.return_value = {'db_url': 'postgresql://test:test@localhost/test'}

        mock_setup.return_value = (mock_connection_params, DatabaseType.POSTGRES)
        mock_construct.return_value = complex_tables

        # Run the command with --singular-names
        result = runner.invoke(
            gen,
            [
                '--db-url',
                'postgresql://test:test@localhost/test',
                '--dir',
                temp_output_dir,
                '--type',
                'pydantic',
                '--framework',
                'fastapi',
                '--singular-names',
            ],
        )

        # Command should succeed
        assert result.exit_code == 0, f'Command failed with output: {result.output}'

        # Check that files were generated
        model_file = find_generated_model_file(temp_output_dir)
        assert model_file is not None, 'Model file was not generated'
        assert model_file.exists(), 'Model file was not generated'

        # Read the generated content
        content = model_file.read_text()

        # Verify complex table names are singularized correctly
        assert 'class UserProfileBaseSchema(' in content, 'UserProfileBaseSchema not found'
        assert 'class UserProfile(' in content, 'UserProfile class not found'
        assert 'class OrderItemBaseSchema(' in content, 'OrderItemBaseSchema not found'
        assert 'class OrderItem(' in content, 'OrderItem class not found'

        # Verify plural forms are not present
        assert 'class UserProfilesBaseSchema(' not in content, 'UserProfilesBaseSchema should not be present'
        assert 'class UserProfiles(' not in content, 'UserProfiles should not be present'
        assert 'class OrderItemsBaseSchema(' not in content, 'OrderItemsBaseSchema should not be present'
        assert 'class OrderItems(' not in content, 'OrderItems should not be present'


@pytest.mark.integration
def test_singular_names_with_crud_models(runner, temp_output_dir, mock_database_setup):
    """Test that CRUD models (Insert/Update) also use singular names."""
    # Run the command with --singular-names
    result = runner.invoke(
        gen,
        [
            '--db-url',
            'postgresql://test:test@localhost/test',
            '--dir',
            temp_output_dir,
            '--type',
            'pydantic',
            '--framework',
            'fastapi',
            '--singular-names',
        ],
    )

    # Command should succeed
    assert result.exit_code == 0, f'Command failed with output: {result.output}'

    # Check that files were generated
    model_file = find_generated_model_file(temp_output_dir)
    assert model_file is not None, 'Model file was not generated'
    assert model_file.exists(), 'Model file was not generated'

    # Read the generated content
    content = model_file.read_text()

    # Verify CRUD models use singular names
    assert 'class UserInsert(' in content, 'UserInsert not found'
    assert 'class UserUpdate(' in content, 'UserUpdate not found'
    assert 'class ProductInsert(' in content, 'ProductInsert not found'
    assert 'class ProductUpdate(' in content, 'ProductUpdate not found'
    assert 'class CategoryInsert(' in content, 'CategoryInsert not found'
    assert 'class CategoryUpdate(' in content, 'CategoryUpdate not found'

    # Verify plural CRUD models are not present
    assert 'class UsersInsert(' not in content, 'UsersInsert should not be present'
    assert 'class UsersUpdate(' not in content, 'UsersUpdate should not be present'
    assert 'class ProductsInsert(' not in content, 'ProductsInsert should not be present'
    assert 'class ProductsUpdate(' not in content, 'ProductsUpdate should not be present'


@pytest.mark.integration
def test_singular_names_with_no_crud_models(runner, temp_output_dir, mock_database_setup):
    """Test singular names when CRUD models are disabled."""
    # Run the command with --singular-names and --no-crud-models
    result = runner.invoke(
        gen,
        [
            '--db-url',
            'postgresql://test:test@localhost/test',
            '--dir',
            temp_output_dir,
            '--type',
            'pydantic',
            '--framework',
            'fastapi',
            '--singular-names',
            '--no-crud-models',
        ],
    )

    # Command should succeed
    assert result.exit_code == 0, f'Command failed with output: {result.output}'

    # Check that files were generated
    model_file = find_generated_model_file(temp_output_dir)
    assert model_file is not None, 'Model file was not generated'
    assert model_file.exists(), 'Model file was not generated'

    # Read the generated content
    content = model_file.read_text()

    # Verify base schemas and main classes use singular names
    assert 'class UserBaseSchema(' in content, 'UserBaseSchema not found'
    assert 'class User(' in content, 'User class not found'
    assert 'class ProductBaseSchema(' in content, 'ProductBaseSchema not found'
    assert 'class Product(' in content, 'Product class not found'

    # Verify no CRUD models are generated (as expected with --no-crud-models)
    assert 'class UserInsert(' not in content, 'UserInsert should not be present with --no-crud-models'
    assert 'class UserUpdate(' not in content, 'UserUpdate should not be present with --no-crud-models'
    assert 'class ProductInsert(' not in content, 'ProductInsert should not be present with --no-crud-models'
    assert 'class ProductUpdate(' not in content, 'ProductUpdate should not be present with --no-crud-models'


@pytest.mark.integration
def test_singular_names_backward_compatibility(runner, temp_output_dir, mock_database_setup):
    """Test that existing functionality is not broken by the singular names feature."""
    # Test various combinations to ensure backward compatibility
    test_cases = [
        # (args, should_have_singular, description)
        (['--singular-names'], True, 'with --singular-names'),
        ([], False, 'without --singular-names (default)'),
        (['--singular-names', '--no-crud-models'], True, 'with --singular-names and --no-crud-models'),
        (['--no-crud-models'], False, 'with --no-crud-models only'),
    ]

    for args, should_have_singular, description in test_cases:
        # Create a unique subdirectory for each test case
        case_dir = Path(temp_output_dir) / f'case_{len(args)}'
        case_dir.mkdir(exist_ok=True)

        # Run the command
        cmd_args = [
            '--db-url',
            'postgresql://test:test@localhost/test',
            '--dir',
            str(case_dir),
            '--type',
            'pydantic',
            '--framework',
            'fastapi',
        ] + args

        result = runner.invoke(gen, cmd_args)

        # Command should succeed
        assert result.exit_code == 0, f'Command failed {description} with output: {result.output}'

        # Check that files were generated
        model_file = find_generated_model_file(case_dir)
        assert model_file is not None, f'Model file was not generated {description}'
        assert model_file.exists(), f'Model file was not generated {description}'

        # Read the generated content
        content = model_file.read_text()

        if should_have_singular:
            # Should have singular names
            assert 'class User(' in content, f'User class not found {description}'
            assert 'class Users(' not in content, f'Users class found {description} (should be singular)'
        else:
            # Should have plural names (default)
            assert 'class Users(' in content, f'Users class not found {description}'
            assert 'class User(' not in content, f'User class found {description} (should be plural)'
