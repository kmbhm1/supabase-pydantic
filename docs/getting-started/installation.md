# Installation

To install the package, you can use the following command:

```bash
pip install supabase-pydantic
```

There are a few evolving dependencies that will need to be installed as well & to take note of:

- [pydantic](https://pydantic-docs.helpmanual.io/)-v2: A data validation and settings management using Python type annotations. We may integrate for v1 in the future.
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/): A PostgreSQL database adapter for Python. We will likely integrate a more robust adapter in the future, possibly integrating the lower-level [asyncpg](https://pypi.org/project/asyncpg/) or golang client with Supabase. Other database connections will be added in the future as well.
- [types-psycopg2](https://pypi.org/project/types-psycopg2/): Type hints for psycopg2.
- [faker](https://pypi.org/project/Faker/): A Python package that generates fake data. This package will be critical for adding a future feature to generate seed data.

If you have Python 3.10+ installed, you should be fine, but please [report](https://github.com/kmbhm1/supabase-pydantic/issues/new/choose) any issues you encounter.

The package will (soon, tbd) be available in [conda](https://docs.conda.io/en/latest/) under [conda-forge](https://conda-forge.org/): 

```bash
conda install -c conda-forge supabase-pydantic
```

## Install from source

To install the package from source, you can use the following command:

```bash
pip install git+https://github.com/kmbhm1/supabase-pydantic.git@main
```