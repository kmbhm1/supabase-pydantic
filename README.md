# Supabase Pydantic Schemas

A project for generating Pydantic (& other) models from Supabase (& other) databases. Currently, this is ideal for integrating [FastAPI](https://fastapi.tiangolo.com/) with [supabase-py](https://supabase.com/docs/reference/python/introduction) as a primary use-case, but more updates are coming! This project is a inspired by the TS [type generating](https://supabase.com/docs/guides/api/rest/generating-types) capabilities of supabase cli. Its aim is to provide a similar experience for Python developers.

## Installation

```bash
$ pip install supabase-pydantic                 # install
$ touch .env                                    # create .env file
$ echo "DB_NAME=<your_db_name>" >> .env         # add your postgres db name
$ echo "DB_USER=<your_db_user>" >> .env         # add your postgres db user
$ echo "DB_PASS=<your_db_password>" >> .env     # add your postgres db password
$ echo "DB_HOST=<your_db_host>" >> .env         # add your postgres db host
$ echo "DB_PORT=<your_db_port>" >> .env         # add your postgres db port
```

## Usage

Generate Pydantic models for FastAPI:

```bash
$ sb-pydantic gen --type pydantic --framework fastapi --local
PostGres connection is open.
PostGres connection is closed.
Generating FastAPI Pydantic models...
FastAPI Pydantic models generated successfully: /path/to/your/project/entities/fastapi/schemas.py
File formatted successfully: /path/to/your/project/entities/fastapi/schemas.py
```
