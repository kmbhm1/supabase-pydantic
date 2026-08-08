# Supabase Pydantic Schemas

[![PyPI Version](https://img.shields.io/pypi/v/supabase-pydantic)](https://pypi.org/project/supabase-pydantic/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/supabase-pydantic)
](https://anaconda.org/conda-forge/supabase-pydantic)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
![GitHub License](https://img.shields.io/github/license/kmbhm1/supabase-pydantic)
[![codecov](https://codecov.io/github/kmbhm1/supabase-pydantic/graph/badge.svg?token=PYOJPJTOLM)](https://codecov.io/github/kmbhm1/supabase-pydantic)
![PePy Downloads](https://static.pepy.tech/badge/supabase-pydantic)
![PyPI - Downloads](https://img.shields.io/pypi/dm/supabase-pydantic)

A project for generating Pydantic and SQLAlchemy models from Supabase and MySQL databases. This tool bridges the gap between your database schema and your Python code, providing type-safe models for FastAPI and other frameworks.

Currently, this is ideal for integrating [FastAPI](https://fastapi.tiangolo.com/) with [supabase-py](https://supabase.com/docs/reference/python/introduction) as a primary use-case. This project is inspired by the TS [type generating](https://supabase.com/docs/guides/api/rest/generating-types) capabilities of supabase cli. Its aim is to provide a similar experience for Python developers.

> **Project status (August 2026): maintenance mode.** supabase-pydantic continues to receive bug fixes and dependency updates; nothing is being removed, and no end-of-life date has been set. New feature work has moved to [**castiron**](https://github.com/kmbhm1/castiron), its successor, which carries this project's schema-fidelity engine onto a source-agnostic architecture.
>
> castiron is **0.1.0 and pre-alpha**: today it reads the OpenAPI document a Supabase/PostgREST project publishes — no database connection, no driver — and emits Pydantic v2 models. It does **not** yet connect to a live database, emit SQLAlchemy models, read MySQL, or generate seed data, all of which supabase-pydantic does today. If you rely on those, stay here for now.
>
> Install with `pip install cast-iron` (the distribution is hyphenated; the command and the import package are `castiron`). [Docs](https://kmbhm1.github.io/castiron/) · [Repo](https://github.com/kmbhm1/castiron) · [What this means for supabase-pydantic users](https://kmbhm1.github.io/supabase-pydantic/getting-started/castiron/)

> **📣 NEW (Aug 2025)**: MySQL support! Generate models directly from MySQL databases with the `--db-type mysql` flag. [See the docs](https://kmbhm1.github.io/supabase-pydantic/examples/mysql-support/)
>
> **📣 NEW (Aug 2025)**: SQLAlchemy models with Insert and Update variants for better type safety. [Learn more](https://kmbhm1.github.io/supabase-pydantic/examples/sqlalchemy-models/)

## Installation

```bash
# Install with pip
$ pip install supabase-pydantic

# Or with conda
$ conda install -c conda-forge supabase-pydantic
```

## Configuration

Create a `.env` file with your database connection details:

```bash
DB_NAME=<your_db_name>
DB_USER=<your_db_user>
DB_PASS=<your_db_password>
DB_HOST=<your_db_host>
DB_PORT=<your_db_port>
```

## Usage

### Generate Pydantic Models

Example with full command output (using a local connection):

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --local

2025-08-18 15:47:42 - INFO - supabase_pydantic.db.connection:check_connection:72 - PostGres connection is open.
2025-08-18 15:47:42 - INFO - supabase_pydantic.db.connection:construct_tables:136 - Processing schema: public
2025-08-18 15:47:42 - INFO - supabase_pydantic.db.connection:__exit__:105 - PostGres connection is closed.
2025-08-18 15:47:42 - INFO - supabase_pydantic.cli.commands.gen:gen:239 - Generating Pydantic models...
2025-08-18 15:47:42 - INFO - supabase_pydantic.cli.commands.gen:gen:251 - Pydantic models generated successfully for schema 'public': /path/to/your/project/entities/fastapi/schema_public_latest.py
2025-08-18 15:47:42 - INFO - supabase_pydantic.cli.commands.gen:gen:258 - File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
```

### Common Commands

**Using a database URL:**
```bash
$ sb-pydantic gen --type pydantic --framework fastapi --db-url postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

**Generating models for specific schemas:**
```bash
$ sb-pydantic gen --type pydantic --framework fastapi --local --schema extensions --schema auth
```

**Generate SQLAlchemy models:**
```bash
$ sb-pydantic gen --type sqlalchemy --local
```

**Using MySQL:**
```bash
$ sb-pydantic gen --type pydantic --framework fastapi --db-type mysql --db-url mysql://user:pass@localhost:3306/dbname
```

### Makefile Integration

```makefile
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

For full documentation, visit [our docs site](https://kmbhm1.github.io/supabase-pydantic/).
