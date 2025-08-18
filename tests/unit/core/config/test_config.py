"""Tests for configuration utilities in supabase_pydantic.core.config."""

from supabase_pydantic.core.config import (
    WriterConfig,
    get_standard_jobs,
    local_default_env_configuration,
)


import pytest


@pytest.mark.unit
@pytest.mark.config
def test_get_standard_jobs_returns_jobs():
    models = ('pydantic',)
    frameworks = ('fastapi',)
    dirs: dict[str, str | None] = {
        'fastapi': 'fastapi_directory',
    }
    schemas = ('public',)

    job_dict = get_standard_jobs(models, frameworks, dirs, schemas)

    assert 'public' in job_dict
    jobs = job_dict['public']
    assert all([isinstance(job, WriterConfig) for job in jobs.values()])


@pytest.mark.unit
@pytest.mark.config
def test_local_default_env_configuration():
    env_vars = local_default_env_configuration()
    assert env_vars == {
        'DB_NAME': 'postgres',
        'DB_USER': 'postgres',
        'DB_PASS': 'postgres',
        'DB_HOST': 'localhost',
        'DB_PORT': '54322',
    }
