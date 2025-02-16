from unittest.mock import MagicMock, patch

import pytest

# Import the abstract classes
from supabase_pydantic.util.writers.abstract_classes import AbstractClassWriter, AbstractFileWriter, TableInfo


class ConcreteClassWriter(AbstractClassWriter):
    def write_operational_class(self):
        return 'OperationalClassDefinition'

    def write_name(self):
        return 'ConcreteClassName'

    def write_metaclass(self, metaclasses=None):
        return 'MetaClass' if metaclasses else None

    def write_docs(self):
        return '\nClass documentation'

    def write_primary_keys(self):
        return '\nPrimaryKeyDefinition'

    def write_primary_columns(self):
        return '\nPrimaryColumnsDefinition'

    def write_foreign_columns(self, use_base=False):
        return '\nForeignColumnsDefinition' if use_base else None


class DummyClassWriter(AbstractClassWriter):
    pass


class NotImplementClassWriter(AbstractClassWriter):
    def write_name(self):
        return super().write_name()

    def write_operational_class(self):
        return super().write_operational_class()

    def write_metaclass(self, metaclasses=None):
        return super().write_metaclass(metaclasses)

    def write_docs(self):
        return super().write_docs()

    def write_primary_keys(self):
        return super().write_primary_keys()

    def write_primary_columns(self):
        return super().write_primary_columns()

    def write_foreign_columns(self, use_base=False):
        return super().write_foreign_columns(use_base)


def test_abstract_class_writer_write_class():
    """Test the write_class method of the AbstractClassWriter."""
    # Setup
    table_info = TableInfo(name='test_table', columns=[])
    writer = ConcreteClassWriter(table=table_info)

    # Execute
    class_definition = writer.write_class(add_fk=True)

    # Verify
    expected_output = (
        'class ConcreteClassName:\nClass documentation\nPrimaryKeyDefinition\n\n\nPrimaryColumnsDefinition'
    )
    assert class_definition == expected_output
    assert writer._proper_name('test_table') == 'TestTable'
    assert writer.write_operational_class() == 'OperationalClassDefinition'


def test_concrete_class_writer_methods():
    """Test the methods of the ConcreteClassWriter."""
    table_info = TableInfo(name='test_table', columns=[])
    writer = ConcreteClassWriter(table=table_info)

    assert writer.write_name() == 'ConcreteClassName'
    assert writer.write_operational_class() == 'OperationalClassDefinition'
    assert writer.column_section('Comment', ['Column1', 'Column2']) == '\t# Comment\n\tColumn1\n\tColumn2'


def test_abstract_class_writer_type_error_on_implementation():
    """Test that a TypeError is raised when the abstract methods are not implemented."""
    table_info = TableInfo(name='test_table', columns=[])

    with pytest.raises(TypeError):
        _ = DummyClassWriter(table=table_info)


def test_abstract_class_writer_not_implemented_error():
    """Test that NotImplementedError is raised when the abstract methods are called."""
    table_info = TableInfo(name='test_table', columns=[])
    writer = NotImplementClassWriter(table=table_info)

    with pytest.raises(NotImplementedError):
        writer.write_name()

    assert writer.write_operational_class() is None

    with pytest.raises(NotImplementedError):
        writer.write_metaclass()

    with pytest.raises(NotImplementedError):
        writer.write_docs()

    with pytest.raises(NotImplementedError):
        writer.write_primary_keys()

    with pytest.raises(NotImplementedError):
        writer.write_primary_columns()

    with pytest.raises(NotImplementedError):
        writer.write_foreign_columns()


class ConcreteFileWriter(AbstractFileWriter):
    def __init__(self, tables, file_path, writer):
        super().__init__(tables, file_path, writer)

    def write_imports(self) -> str:
        return 'Imports'

    def write_custom_classes(self) -> str | None:
        return 'CustomClasses'

    def write_base_classes(self) -> str | None:
        return 'BaseClasses'

    def write_operational_classes(self) -> str | None:
        return 'OperationalClasses'


class DummyFileWriter(AbstractFileWriter):
    pass


class NotImplementFileWriter(AbstractFileWriter):
    def write_imports(self) -> str:
        return super().write_imports()

    def write_custom_classes(self) -> str | None:
        return super().write_custom_classes()

    def write_base_classes(self) -> str | None:
        return super().write_base_classes()

    def write_operational_classes(self) -> str | None:
        return super().write_operational_classes()


def test_abstract_file_writer_write():
    """Test the write method of the AbstractFileWriter."""
    tables = [TableInfo(name='test_table', columns=[])]
    writer = ConcreteFileWriter(tables=tables, file_path='test.py', writer=ConcreteClassWriter)

    file_content = writer.write()

    expected_output = 'Imports\n\n\nCustomClasses\n\n\nBaseClasses\n\n\nOperationalClasses\n'
    assert file_content == expected_output
    assert writer.join(['a', 'b', 'c']) == 'a\n\n\nb\n\n\nc'


def test_concrete_file_writer_methods():
    """Test the methods of the ConcreteFileWriter."""
    tables = [TableInfo(name='test_table', columns=[])]
    writer = ConcreteFileWriter(tables=tables, file_path='test.py', writer=ConcreteClassWriter)

    assert writer.write_imports() == 'Imports'
    assert writer.write_custom_classes() == 'CustomClasses'
    assert writer.write_base_classes() == 'BaseClasses'
    assert writer.write_operational_classes() == 'OperationalClasses'


def test_save_method():
    tables = [TableInfo(name='test_table', columns=[])]
    writer = ConcreteFileWriter(tables, 'directory/test_file.py', MagicMock(spec=AbstractClassWriter))

    with (
        patch('builtins.open', new_callable=MagicMock) as mock_open,
        patch('pathlib.Path.exists', return_value=True),
        patch(
            'supabase_pydantic.util.writers.abstract_classes.generate_unique_filename',
            return_value='test_file_unique.py',
        ) as mock_unique_filename,
    ):
        result = writer.save(overwrite=False)

        # Assert the generate_unique_filename was called correctly
        mock_unique_filename.assert_called_once_with('test_file', '.py', 'directory')

        # Assert the file was opened with the correct filename and mode
        mock_open.assert_called_with('test_file_unique.py', 'w')

        # Assert the correct path is returned
        assert result == ('directory/test_file_latest.py', 'test_file_unique.py')


def test_abstract_file_writer_type_error_on_implementation():
    """Test that a TypeError is raised when the abstract methods are not implemented."""
    tables = [TableInfo(name='test_table', columns=[])]
    with pytest.raises(TypeError):
        _ = DummyFileWriter(tables=tables, file_path='test.py', writer=ConcreteClassWriter)


def test_abstract_file_writer_not_implemented_error():
    """Test that NotImplementedError is raised when the abstract methods are called."""
    tables = [TableInfo(name='test_table', columns=[])]
    writer = NotImplementFileWriter(tables=tables, file_path='test.py', writer=ConcreteClassWriter)

    with pytest.raises(NotImplementedError):
        writer.write_imports()

    with pytest.raises(NotImplementedError):
        writer.write_custom_classes()

    with pytest.raises(NotImplementedError):
        writer.write_base_classes()

    with pytest.raises(NotImplementedError):
        writer.write_operational_classes()
