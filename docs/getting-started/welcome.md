# Supabase Pydantic

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/supabase-pydantic)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
![GitHub License](https://img.shields.io/github/license/kmbhm1/supabase-pydantic)
[![codecov](https://codecov.io/github/kmbhm1/supabase-pydantic/graph/badge.svg?token=PYOJPJTOLM)](https://codecov.io/github/kmbhm1/supabase-pydantic)
![PyPI - Downloads](https://img.shields.io/pypi/dm/supabase-pydantic)


Supabase Pydantic is a Python library that **generates** Pydantic models for Supabase - more models & database support to come :wink:.  It is designed to enhance the utility of Supabase as an entity for rapid prototyping and development. 

``` bash title="A First Example" hl_lines="1"
$ sb-pydantic gen --type pydantic --framework fastapi --local

PostGres connection is open.
PostGres connection is closed.
Generating FastAPI Pydantic models...
FastAPI Pydantic models generated successfully: /path/to/your/project/entities/fastapi/schemas_latest.py
File formatted successfully: /path/to/your/project/entities/fastapi/schemas_latest.py
```

Some users may find it more convenient to integrate a Makefile command:

``` bash title="Makefile"
gen-types:
    @echo "Generating FastAPI Pydantic models..."
    @sb-pydantic gen --type pydantic --framework fastapi --dir <your path> --local
```

## Why use supabase-pydantic?

The [supabase-py](https://github.com/supabase-community/supabase-py) library currently lacks an automated system to enhance type safety and data validation in Python—a similar, but essential feature that is readily available and highly useful in the JavaScript/TypeScript library, as outlined in [Supabase's documentation](https://supabase.com/docs/reference/javascript/typescript-support#generating-typescript-types).

[Pydantic](https://docs.pydantic.dev/latest/), a popular library for data validation and settings management in Python, leverages type annotations to validate data, significantly enhancing the robustness and clarity of code. While both TypeScript and Pydantic aim to improve type safety and structure within dynamic programming environments, a key distinction is that Pydantic validates data at runtime.

This package aims to bridge the gap, delivering an enriched experience for Python developers with Supabase. It not only replicates the functionalities of the TypeScript library but is also finely tuned to the diverse tools and landscape of the Python community. Moreover, it's designed to turbocharge your workflow, making rapid prototyping not just faster but also a delightful adventure in development.

## The Bennies

1. ***Automated* enhanced type safety**: supabase-pydantic generates Pydantic models for Supabase without the hassle of manual setup, ensuring that your data is validated and structured correctly, requiring less oversight. This feature significantly enhances the robustness of deployment pipelines and clarity of your code, making it easier for you to focus on building your application.

2. **Rapid prototyping**: With supabase-pydantic, you can quickly generate FastAPI Pydantic models, saving you time and effort in setting up your project's schemas, models, etc.

3. **Seamless integration**: supabase-pydantic is intended to integrate seamlessly with development and automated pipelines, allowing you to leverage the power of Supabase while enjoying the benefits of Pydantic's data validation and settings management in a streamlined fashion.

4. **Pythonic experience**: Built specifically for the Python community, supabase-pydantic is finely tuned to the tools and landscape of Python development, providing a familiar and efficient workflow.

5. **Comprehensive documentation**: supabase-pydantic comes with comprehensive documentation, making it easy to get started and explore its features.

