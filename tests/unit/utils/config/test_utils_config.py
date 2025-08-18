import pytest

from supabase_pydantic.core.config import WriterConfig
from supabase_pydantic.core.constants import FrameWorkType, OrmType
from supabase_pydantic.utils.config import get_standard_jobs, local_default_env_configuration


class TestGetStandardJobs:
    def test_get_standard_jobs_with_fastapi_enabled(self):
        models = ("pydantic", "sqlalchemy")
        frameworks = ("fastapi",)
        dirs = {"fastapi": "/path/to/fastapi"}
        schemas = ("public", "custom")

        result = get_standard_jobs(models, frameworks, dirs, schemas)

        assert len(result) == 2  # Two schemas
        assert "public" in result
        assert "custom" in result

        # Check public schema config
        assert "Pydantic" in result["public"]
        assert "SQLAlchemy" in result["public"]

        # Verify Pydantic config
        pydantic_config = result["public"]["Pydantic"]
        assert isinstance(pydantic_config, WriterConfig)
        assert pydantic_config.file_type == OrmType.PYDANTIC
        assert pydantic_config.framework_type == FrameWorkType.FASTAPI
        assert pydantic_config.filename == "schema_public.py"
        assert pydantic_config.directory == "/path/to/fastapi"
        assert pydantic_config.enabled is True

        # Verify SQLAlchemy config
        sqlalchemy_config = result["public"]["SQLAlchemy"]
        assert isinstance(sqlalchemy_config, WriterConfig)
        assert sqlalchemy_config.file_type == OrmType.SQLALCHEMY
        assert sqlalchemy_config.framework_type == FrameWorkType.FASTAPI
        assert sqlalchemy_config.filename == "database_public.py"
        assert sqlalchemy_config.directory == "/path/to/fastapi"
        assert sqlalchemy_config.enabled is True

        # Check custom schema has correct filename
        assert result["custom"]["Pydantic"].filename == "schema_custom.py"
        assert result["custom"]["SQLAlchemy"].filename == "database_custom.py"

    def test_get_standard_jobs_with_partial_models(self):
        models = ("pydantic",)  # Only pydantic, no sqlalchemy
        frameworks = ("fastapi",)
        dirs = {"fastapi": "/path/to/fastapi"}

        result = get_standard_jobs(models, frameworks, dirs)

        assert "public" in result
        assert "Pydantic" in result["public"]
        assert "SQLAlchemy" in result["public"]

        # Pydantic should be enabled, SQLAlchemy disabled
        assert result["public"]["Pydantic"].enabled is True
        assert result["public"]["SQLAlchemy"].enabled is False

    def test_get_standard_jobs_with_no_fastapi_dir(self):
        models = ("pydantic", "sqlalchemy")
        frameworks = ("fastapi",)
        dirs = {}  # No fastapi directory

        result = get_standard_jobs(models, frameworks, dirs)

        assert result == {}  # Should return empty dict since no fastapi dir

    def test_get_standard_jobs_with_none_fastapi_dir(self):
        models = ("pydantic", "sqlalchemy")
        frameworks = ("fastapi",)
        dirs = {"fastapi": None}  # None fastapi directory

        result = get_standard_jobs(models, frameworks, dirs)

        assert result == {}  # Should return empty dict since fastapi dir is None


class TestLocalDefaultEnvConfiguration:
    def test_local_default_env_configuration(self):
        result = local_default_env_configuration()

        assert isinstance(result, dict)
        assert result["DB_NAME"] == "postgres"
        assert result["DB_USER"] == "postgres"
        assert result["DB_PASS"] == "postgres"
        assert result["DB_HOST"] == "localhost"
        assert result["DB_PORT"] == "54322"
