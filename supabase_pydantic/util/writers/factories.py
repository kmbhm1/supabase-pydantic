from supabase_pydantic.util.dataclasses import FrameWorkType, OrmType


class ClassWriterFactory:
    @staticmethod
    def get_class_writer(
        table: str,
        file_type: OrmType = OrmType.PYDANTIC,
        framework_type: FrameWorkType = FrameWorkType.FASTAPI,
        nullify_base_schema_class: bool = False,
    ):
        """Get the class writer based on the provided parameters.

        Args:
            table (str): The table name.
            file_type (OrmType, optional): The ORM type. Defaults to OrmType.PYDANTIC.
            framework_type (FrameWorkType, optional): The framework type. Defaults to FrameWorkType.FASTAPI.
            nullify_base_schema_class (bool, optional): Whether to nullify the base schema class. Defaults to False.

        Returns:
            The class writer instance.
        """  # noqa: E501
        # if file_type == 'SQLAlchemy':
        #     if framework_type == 'FastAPI':
        #         return SQLAlchemyFastAPIClassWriter(table, file_type, framework_type, nullify_base_schema_class)
        #     elif framework_type == 'JSONAPI':
        #         return SQLAlchemyJSONAPIClassWriter(table, file_type, framework_type, nullify_base_schema_class)
        # elif file_type == 'Pydantic':
        #     if framework_type == 'FastAPI':
        #         return PydanticFastAPIClassWriter(table, file_type, framework_type, nullify_base_schema_class)
        #     elif framework_type == 'JSONAPI':
        #         return PydanticJSONAPIClassWriter(table, file_type, framework_type, nullify_base_schema_class)
        # else:
        #     raise ValueError('Unsupported file type or framework type')
        pass


class FileWriterFactory:
    @staticmethod
    def get_file_writer(
        file_type: OrmType = OrmType.PYDANTIC,
        framework_type: FrameWorkType = FrameWorkType.FASTAPI,
    ):
        """Get the file writer based on the provided parameters.

        Args:
            file_type (OrmType, optional): The ORM type. Defaults to OrmType.PYDANTIC.
            framework_type (FrameWorkType, optional): The framework type. Defaults to FrameWorkType.FASTAPI.

        Returns:
            The file writer instance.
        """  # noqa: E501
        pass
