# Generating Pydantic Models with Enums from a Simple Supabase/Postgres Setup

This guide demonstrates how to use `sb-pydantic` to generate Pydantic models with proper enum support from a simple Postgres (or Supabase) schema. You'll see how enum types in your database are automatically turned into Python `Enum` classes and referenced in your models.

---

## Step 1: Define Your Postgres Enums and Tables

Suppose you have the following schema in your Postgres database:

```sql
CREATE TYPE public.us_state AS ENUM ('NY', 'CA', 'TX', 'IN');
CREATE TYPE public.document_status AS ENUM ('draft', 'published', 'archived');

CREATE TABLE public.document (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    state public.us_state NOT NULL,
    status public.document_status NOT NULL
);
```

---

## Step 2: Connect Supabase and Prepare Your Project

1. Make sure your Supabase/Postgres instance is running and accessible.
2. Install `sb-pydantic` and dependencies (see [Installation](../getting-started/installation.md)).
3. Configure your database connection as described in the main docs.

---

## Step 3: Run sb-pydantic to Generate Models

From your project directory, run:

```sh
sb-pydantic gen --type pydantic --framework fastapi --local
```

This will introspect your database and generate Pydantic models in the `entities/fastapi/` directory.

---

## Step 4: Review the Generated Enum Classes and Model Usage

In your generated models (e.g., `entities/fastapi/schema_public_latest.py`), you'll see code like:

```python
from enum import Enum

class PublicUsStateEnum(str, Enum):
    NY = 'NY'
    CA = 'CA'
    TX = 'TX'
    IN_ = 'IN'  # 'IN' is a Python reserved keyword, so an underscore is appended

class PublicDocumentStatusEnum(str, Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

class Document(BaseModel):
    id: int
    name: str
    state: PublicUsStateEnum
    status: PublicDocumentStatusEnum
```

Notice how the column types for `state` and `status` are now the correct enum classes, not just `str`.

---

## Step 5: Using the Models in FastAPI (optional)

You can now use these models directly in your FastAPI endpoints, with full enum validation:

```python
@app.post('/documents')
def create_document(doc: Document):
    # doc.state and doc.status are enum members, e.g., PublicUsStateEnum.NY
    ...
```

---

## Example Output

When you POST JSON like this:

```json
{
  "name": "My Doc",
  "state": "CA",
  "status": "published"
}
```

FastAPI and Pydantic will automatically validate the enum fields and return errors for invalid values.

---

## Summary

With `sb-pydantic`, your Pydantic models will always use the correct enum types, matching your database schema exactly. This improves type safety, validation, and code clarity.
