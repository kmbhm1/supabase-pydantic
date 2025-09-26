from supabase_pydantic.core.constants import FrameWorkType, OrmType
from supabase_pydantic.core.writers.abstract import AbstractFileWriter
from supabase_pydantic.core.writers.pydantic import PydanticFastAPIWriter
from supabase_pydantic.core.writers.sqlalchemy import SqlAlchemyFastAPIWriter
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import TableInfo


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
        disable_model_prefix_protection: bool = False,
        singular_names: bool = False,
        database_type: DatabaseType = DatabaseType.POSTGRES,
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
            disable_model_prefix_protection (bool, optional): Disable Pydantic's "model_" prefix protection. Defaults to False.
            singular_names (bool, optional): Generate class names in singular form. Defaults to False.
            database_type (DatabaseType, optional): The database type. Defaults to DatabaseType.POSTGRES.

        Returns:
            The file writer instance.
        """  # noqa: E501
        match file_type, framework_type:
            case OrmType.SQLALCHEMY, FrameWorkType.FASTAPI:
                return SqlAlchemyFastAPIWriter(
                    tables,
                    file_path,
                    add_null_parent_classes=add_null_parent_classes,
                    singular_names=singular_names,
                    database_type=database_type,
                )
            case OrmType.PYDANTIC, FrameWorkType.FASTAPI:
                return PydanticFastAPIWriter(
                    tables,
                    file_path,
                    add_null_parent_classes=add_null_parent_classes,
                    generate_crud_models=generate_crud_models,
                    generate_enums=generate_enums,
                    disable_model_prefix_protection=disable_model_prefix_protection,
                    singular_names=singular_names,
                    database_type=database_type,
                )
            case _:
                raise ValueError(f'Unsupported file type and framework: {file_type}, {framework_type}')
