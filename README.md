# Supabase Pydantic Schemas

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/supabase-pydantic)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
![GitHub License](https://img.shields.io/github/license/kmbhm1/supabase-pydantic)
[![codecov](https://codecov.io/github/kmbhm1/supabase-pydantic/graph/badge.svg?token=PYOJPJTOLM)](https://codecov.io/github/kmbhm1/supabase-pydantic)
![PyPI - Downloads](https://img.shields.io/pypi/dm/supabase-pydantic)


A project for generating Pydantic (& other) models from Supabase (& other) databases. Currently, this is ideal for integrating [FastAPI](https://fastapi.tiangolo.com/) with [supabase-py](https://supabase.com/docs/reference/python/introduction) as a primary use-case, but more updates are coming! This project is a inspired by the TS [type generating](https://supabase.com/docs/guides/api/rest/generating-types) capabilities of supabase cli. Its aim is to provide a similar experience for Python developers.

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

PostGres connection is open.
PostGres connection is closed.
Generating FastAPI Pydantic models...
FastAPI Pydantic models generated successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
```

Or generate with a url:

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --db-url postgresql://postgres:postgres@127.0.0.1:54322/postgres

Checking local database connection.postgresql://postgres:postgres@127.0.0.1:54322/postgres
Connecting to database: postgres on host: 127.0.0.1 with user: postgres and port: 54322
PostGres connection is open.
Generating FastAPI Pydantic models...
FastAPI Pydantic models generated successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schema_public_latest.py
```

You can generate Pydantic models for certain schemas in your database using the `--schema` or `--all-schemas` options:

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --local --schema extensions --schema auth
```

This command will generate a BaseModel file for each schema in your database.

For some users, integrating a Makefile command may be more convenient:

```bash
gen-types:
    @echo "Generating FastAPI Pydantic models..."
    @sb-pydantic gen --type pydantic --framework fastapi --dir <your path> --local
```
