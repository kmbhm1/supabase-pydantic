from supabase_pydantic.util.constants import FrameWorkType, OrmType
from supabase_pydantic.util.dataclasses import TableInfo
from supabase_pydantic.util.writers.abstract_classes import AbstractFileWriter
from supabase_pydantic.util.writers.pydantic_writers import PydanticFastAPIWriter, PydanticJSONAPIWriter
from supabase_pydantic.util.writers.sqlalchemy_writers import SqlAlchemyFastAPIWriter, SqlAlchemyJSONAPIWriter


class FileWriterFactory:
    @staticmethod
    def get_file_writer(
        tables: list[TableInfo],
        file_path: str,
        file_type: OrmType = OrmType.PYDANTIC,
        framework_type: FrameWorkType = FrameWorkType.FASTAPI,
    ) -> AbstractFileWriter:
        """Get the file writer based on the provided parameters.

        Args:
            tables (list[TableInfo]): The list of tables.
            file_path (str): The file path.
            file_type (OrmType, optional): The ORM type. Defaults to OrmType.PYDANTIC.
            framework_type (FrameWorkType, optional): The framework type. Defaults to FrameWorkType.FASTAPI.

        Returns:
            The file writer instance.
        """  # noqa: E501
        match file_type, framework_type:
            case OrmType.SQLALCHEMY, FrameWorkType.FASTAPI:
                return SqlAlchemyFastAPIWriter(tables, file_path)
            case OrmType.SQLALCHEMY, FrameWorkType.FASTAPI_JSONAPI:
                return SqlAlchemyJSONAPIWriter(tables, file_path)
            case OrmType.PYDANTIC, FrameWorkType.FASTAPI:
                return PydanticFastAPIWriter(tables, file_path)
            case OrmType.PYDANTIC, FrameWorkType.FASTAPI_JSONAPI:
                return PydanticJSONAPIWriter(tables, file_path)
            case _:
                raise ValueError(f'Unsupported file type or framework type: {file_type}, {framework_type}')
