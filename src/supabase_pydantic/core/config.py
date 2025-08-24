import os
from dataclasses import dataclass

from supabase_pydantic.core.constants import FrameWorkType, OrmType
from supabase_pydantic.db.database_type import DatabaseType


@dataclass
class WriterConfig:
    file_type: OrmType
    framework_type: FrameWorkType
    filename: str
    directory: str
    enabled: bool

    def ext(self) -> str:
        """Get the file extension based on the file name."""
        return self.filename.split('.')[-1]

    def name(self) -> str:
        """Get the file name without the extension."""
        return self.filename.split('.')[0]

    def fpath(self) -> str:
        """Get the full file path."""
        return os.path.join(self.directory, self.filename)

    def to_dict(self) -> dict[str, str]:
        """Convert the WriterConfig object to a dictionary."""
        return {
            'file_type': str(self.file_type),
            'framework_type': str(self.framework_type),
            'filename': self.filename,
            'directory': self.directory,
            'enabled': str(self.enabled),
        }


# job helpers
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


def local_default_env_configuration(db_type: DatabaseType = DatabaseType.POSTGRES) -> dict[str, str | None]:
    """Get the environment variables for a local connection.

    Args:
        db_type: Database type (POSTGRES or MYSQL)

    Returns:
        Dict of environment variables with default values for local connection
    """
    if db_type == DatabaseType.MYSQL:
        return {
            'DB_NAME': 'mysql',
            'DB_USER': 'root',
            'DB_PASS': 'password',
            'DB_HOST': 'localhost',
            'DB_PORT': '3306',
        }
    else:  # default to postgres
        return {
            'DB_NAME': 'postgres',
            'DB_USER': 'postgres',
            'DB_PASS': 'postgres',
            'DB_HOST': 'localhost',
            'DB_PORT': '54322',
        }
