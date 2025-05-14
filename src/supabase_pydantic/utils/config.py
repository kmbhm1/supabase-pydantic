"""Configuration utilities for generators and jobs."""

from src.supabase_pydantic.db.constants import FrameWorkType, OrmType, WriterConfig


def get_standard_jobs(
    models: tuple[str], frameworks: tuple[str], dirs: dict[str, str | None], schemas: tuple[str, ...] = ('public',)
) -> dict[str, dict[str, WriterConfig]]:
    """Get the standard jobs for the writer."""

    jobs: dict[str, dict[str, WriterConfig]] = {}

    for schema in schemas:
        # Set the file names
        pydantic_fname, sqlalchemy_fname = f'schema_{schema}.py', f'database_{schema}.py'

        # Add the jobs
        if 'fastapi' in dirs and dirs['fastapi'] is not None:
            jobs[schema] = {
                'Pydantic': WriterConfig(
                    file_type=OrmType.PYDANTIC,
                    framework_type=FrameWorkType.FASTAPI,
                    filename=pydantic_fname,
                    directory=dirs['fastapi'],
                    enabled='pydantic' in models and 'fastapi' in frameworks,
                ),
                'SQLAlchemy': WriterConfig(
                    file_type=OrmType.SQLALCHEMY,
                    framework_type=FrameWorkType.FASTAPI,
                    filename=sqlalchemy_fname,
                    directory=dirs['fastapi'],
                    enabled='sqlalchemy' in models and 'fastapi' in frameworks,
                ),
            }

    return jobs
