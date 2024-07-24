from abc import ABC, abstractmethod


class AbstractTableClassWriter(ABC):
    def __init__(self, table, nullify_base_schema_class):
        self.table = table
        self.nullify_base_schema_class = nullify_base_schema_class

    @abstractmethod
    def write(self):
        """Method to write the complete class definition."""
        return self.write_name() + self.write_docs() + self.write_columns() + self.write_foreign_columns()

    @abstractmethod
    def write_name(self):
        """Method to generate the header for the base class."""
        raise NotImplementedError('write_name not implemented')

    @abstractmethod
    def write_docs(self):
        """Method to generate the docstrings for the class."""
        raise NotImplementedError('write_docs not implemented')

    @abstractmethod
    def write_columns(self):
        """Method to generate column definitions for the class."""
        raise NotImplementedError('write_columns not implemented')

    @abstractmethod
    def write_foreign_column(self, fk, is_base=False, is_view=False, is_nullable=True):
        """Method to generate foreign table relations in the class."""
        raise NotImplementedError('write_foreign_column not implemented')


class AbstractFileWriter(ABC):
    def __init__(self, file_path, table_class_writer):
        self.file_path = file_path
        self.table_class_writer = table_class_writer

    @abstractmethod
    def write(self):
        """Method to write the complete file."""
        return (
            self.write_imports()
            + self.write_custom_classes()
            + self.write_base_classes()
            + self.write_operational_classes()
        )

    @abstractmethod
    def write_imports(self):
        """Method to generate import statements for the file."""
        raise NotImplementedError('write_imports not implemented')

    @abstractmethod
    def write_custom_classes(self):
        """Method to generate custom class definitions for the file."""
        raise NotImplementedError('write_custom_classes not implemented')

    @abstractmethod
    def write_base_classes(self):
        """Method to generate class definitions for the file."""
        raise NotImplementedError('write_classes not implemented')

    @abstractmethod
    def write_operational_classes(self):
        """Method to generate operational class definitions for the file."""
        raise NotImplementedError('write_operational_classes not implemented')
