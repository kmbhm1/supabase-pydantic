# Supabase Pydantic Schemas

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/supabase-pydantic)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
![GitHub License](https://img.shields.io/github/license/kmbhm1/supabase-pydantic)
[![codecov](https://codecov.io/github/kmbhm1/supabase-pydantic/graph/badge.svg?token=PYOJPJTOLM)](https://codecov.io/github/kmbhm1/supabase-pydantic)
![PePy Downloads](https://static.pepy.tech/badge/supabase-pydantic)


A project for generating Pydantic (& other) models from Supabase (& other) databases. Currently, this is ideal for integrating [FastAPI](https://fastapi.tiangolo.com/) with [supabase-py](https://supabase.com/docs/reference/python/introduction) as a primary use-case, but more updates are coming! This project is a inspired by the TS [type generating](https://supabase.com/docs/guides/api/rest/generating-types) capabilities of supabase cli. Its aim is to provide a similar experience for Python developers.

> **📣 NEW (Feb 2025)**: Generated SQLAlchemy models now include Insert and Update variants for better type safety and validation. [Learn more](https://kmbhm1.github.io/supabase-pydantic/examples/insert-update-models/)

## Installation

We recommend installing the package using pip:

```bash
$ pip install supabase-pydantic
```

Installing with conda is also available:

```bash
conda install -c conda-forge supabase-pydantic
```

## Configuration

```bash
$ touch .env                                    # create .env file
$ echo "DB_NAME=<your_db_name>" >> .env         # add your postgres db name
$ echo "DB_USER=<your_db_user>" >> .env         # add your postgres db user
$ echo "DB_PASS=<your_db_password>" >> .env     # add your postgres db password
$ echo "DB_HOST=<your_db_host>" >> .env         # add your postgres db host
$ echo "DB_PORT=<your_db_port>" >> .env         # add your postgres db port
```

## Usage

Generate Pydantic models for FastAPI using a local supabase connection:

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --local

2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:72 - PostGres connection is open.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:construct_tables:136 - Processing schema: public
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:__exit__:105 - PostGres connection is closed.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:239 - Generating Pydantic models...
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:251 - Pydantic models generated successfully for schema 'public': /path/to/your/project/entities/fastapi/schema_public_latest.py
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:258 - File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
```

Or generate with a url:

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --db-url postgresql://postgres:postgres@127.0.0.1:54322/postgres

2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:72 - Checking local database connection: postgresql://postgres:postgres@127.0.0.1:54322/postgres
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:75 - Connecting to database: postgres on host: 127.0.0.1 with user: postgres and port: 54322
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:72 - PostGres connection is open.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:construct_tables:136 - Processing schema: public
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:__exit__:105 - PostGres connection is closed.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:239 - Generating Pydantic models...
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:251 - Pydantic models generated successfully for schema 'public': /path/to/your/project/entities/fastapi/schema_public_latest.py
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:258 - File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
```

You can generate Pydantic models for certain schemas in your database using the `--schema` or `--all-schemas` options:

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --local --schema extensions --schema auth
```

This command will generate a BaseModel file for each schema in your database.

### Generate SQLAlchemy ORM Models

To generate SQLAlchemy models with Insert and Update variants:

```bash
$ sb-pydantic gen --type sqlalchemy --local

2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:72 - PostGres connection is open.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:construct_tables:136 - Processing schema: public
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:__exit__:105 - PostGres connection is closed.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:239 - Generating SQLAlchemy models...
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:251 - SQLAlchemy models generated successfully for schema 'public': /path/to/your/project/entities/sqlalchemy/schema_public_latest.py
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:258 - File formatted successfully: /path/to/your/project/entities/sqlalchemy/schema_public_latest.py
```

Or with a specific database URL:

```bash
$ sb-pydantic gen --type sqlalchemy --db-url postgresql://postgres:postgres@127.0.0.1:54322/postgres

2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:72 - Checking local database connection: postgresql://postgres:postgres@127.0.0.1:54322/postgres
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:75 - Connecting to database: postgres on host: 127.0.0.1 with user: postgres and port: 54322
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:check_connection:72 - PostGres connection is open.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:construct_tables:136 - Processing schema: public
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.db.connection:__exit__:105 - PostGres connection is closed.
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:239 - Generating SQLAlchemy models...
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:251 - SQLAlchemy models generated successfully for schema 'public': /path/to/your/project/entities/sqlalchemy/schema_public_latest.py
2025-08-18 15:47:42 | Level 20 | supabase_pydantic.cli.commands.gen:gen:258 - File formatted successfully: /path/to/your/project/entities/sqlalchemy/schema_public_latest.py
```

For some users, integrating Makefile commands may be more convenient:

```bash
# Makefile examples for both Pydantic and SQLAlchemy generation

gen-pydantic:
    @echo "Generating FastAPI Pydantic models..."
    @sb-pydantic gen --type pydantic --framework fastapi --dir ./entities/fastapi --local

gen-sqlalchemy:
    @echo "Generating SQLAlchemy ORM models..."
    @sb-pydantic gen --type sqlalchemy --dir ./entities/sqlalchemy --local

# Generate all model types at once
gen-all: gen-pydantic gen-sqlalchemy
    @echo "All models generated successfully."
```
