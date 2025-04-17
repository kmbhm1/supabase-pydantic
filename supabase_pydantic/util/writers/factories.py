from supabase_pydantic.util.constants import FrameWorkType, OrmType
from supabase_pydantic.util.dataclasses import TableInfo
from supabase_pydantic.util.writers.abstract_classes import AbstractFileWriter
from supabase_pydantic.util.writers.pydantic_writers import PydanticFastAPIWriter
from supabase_pydantic.util.writers.sqlalchemy_writers import SqlAlchemyFastAPIWriter


class FileWriterFactory:
    @staticmethod
    def get_file_writer(
        tables: list[TableInfo],
        file_path: str,
        file_type: OrmType = OrmType.PYDANTIC,
        framework_type: FrameWorkType = FrameWorkType.FASTAPI,
        add_null_parent_classes: bool = False,
        generate_crud_models: bool = True,
        generate_enums: bool = True,
    ) -> AbstractFileWriter:
        """Get the file writer based on the provided parameters.

        Args:
            tables (list[TableInfo]): The list of tables.
            file_path (str): The file path.
            file_type (OrmType, optional): The ORM type. Defaults to OrmType.PYDANTIC.
            framework_type (FrameWorkType, optional): The framework type. Defaults to FrameWorkType.FASTAPI.
            add_null_parent_classes (bool, optional): Add null parent classes for base classes. Defaults to False.
            generate_crud_models (bool, optional): Generate CRUD models. (i.e., Insert, Update) Defaults to True.
            generate_enums (bool, optional): Generate Enum classes for enum columns. Defaults to True.

        Returns:
            The file writer instance.
        """  # noqa: E501
        match file_type, framework_type:
            case OrmType.SQLALCHEMY, FrameWorkType.FASTAPI:
                return SqlAlchemyFastAPIWriter(tables, file_path)
            case OrmType.PYDANTIC, FrameWorkType.FASTAPI:
                return PydanticFastAPIWriter(
                    tables,
                    file_path,
                    add_null_parent_classes=add_null_parent_classes,
                    generate_crud_models=generate_crud_models,
                    generate_enums=generate_enums,
                )
            case _:
                raise ValueError(f'Unsupported file type or framework type: {file_type}, {framework_type}')
