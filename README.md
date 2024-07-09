# Supabase Pydantic Schemas

A project for digesting Supabase (or Postgres) table & view schemas into Pydantic models. Currently, this is ideal for projects that integrate [FastAPI](https://fastapi.tiangolo.com/) with [Supabase-Python](https://supabase.com/docs/reference/python/introduction), but more updates are coming soon ...

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

```bash
$ sbpyd  # generate default schemas.py to ./entities/fastapi
```

## References

- [Inspiration](https://github.com/yngvem/python-project-structure) for the project structure.
- Github Actions [inspiration](https://endjin.com/blog/2023/02/how-to-implement-continuous-deployment-of-python-packages-with-github-actions) for CI/CD.
