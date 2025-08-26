# Model Prefix Protection in Pydantic Models

This example demonstrates how to use the configurable model prefix protection feature in supabase-pydantic.

## Background

Pydantic v2 reserves the "model_" prefix in its protected namespace, which means fields like `model_id`, `model_name`, or `model_version` would cause errors in Pydantic models. By default, supabase-pydantic renames such fields with a "field_" prefix (e.g., `field_model_id`) and adds the original name as an alias.

This can cause issues in automated processes that expect field names to match database column names directly.

## Setting Up a Test Database

### Create Database Objects

Let's create a test database table with columns that have the "model_" prefix:

```sql title="model_prefix_setup.sql"
-- Create test table with model_ prefixed columns
CREATE TABLE model_test_items (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    model_type TEXT,
    model_version VARCHAR(50),
    model_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert some sample data
INSERT INTO model_test_items (name, model_type, model_version, model_id) 
VALUES 
    ('Item 1', 'product', 'v1.0', gen_random_uuid()),
    ('Item 2', 'service', 'v2.3.1', gen_random_uuid()),
    ('Item 3', 'component', 'v0.9.5', gen_random_uuid());

-- Create a view to demonstrate the feature with views
CREATE VIEW model_test_items_view AS
SELECT 
    id,
    name,
    model_type,
    model_version,
    model_id,
    created_at,
    updated_at
FROM model_test_items;

-- Grant necessary permissions if needed
-- GRANT SELECT, INSERT, UPDATE, DELETE ON model_test_items TO your_user;
-- GRANT SELECT ON model_test_items_view TO your_user;
```

To run this setup script:

```bash title="Run setup script"
$ psql -d your_database -f model_prefix_setup.sql

CREATE TABLE
INSERT 0 3
CREATE VIEW
```

## Default Behavior (Protection Enabled)

By default, supabase-pydantic will protect against Pydantic's reserved "model_" prefix by renaming fields and using aliases:

```bash title="Generate models with default protection"
$ supabase-pydantic gen --schema public --uri postgresql://user:password@localhost:5432/your_database

2023-07-15 10:42:18 - INFO - PostGres connection is open.
2023-07-15 10:42:19 - INFO - PostGres connection is closed.
2023-07-15 10:42:19 - INFO - Generating models...
2023-07-15 10:42:22 - INFO - Models generated successfully: /path/to/your/project/models.py
2023-07-15 10:42:22 - INFO - File formatted successfully: /path/to/your/project/models.py
```

The generated model will include aliased fields:

```python title="Generated model with default protection"
class ModelTestItemsBaseSchema(CustomModel):
    """ModelTestItems Base Schema."""

    # Primary Keys
    id: int

    # Columns
    created_at: datetime.datetime | None = Field(default=None)
    field_model_id: UUID4 | None = Field(default=None, alias='model_id')
    field_model_type: str | None = Field(default=None, alias='model_type')
    field_model_version: str | None = Field(default=None, alias='model_version')
    name: str
    updated_at: datetime.datetime | None = Field(default=None)
```

## Disabling Model Prefix Protection

To disable this protection and use the original column names directly in your models:

```bash title="Generate models with protection disabled"
$ supabase-pydantic gen --schema public --uri postgresql://user:password@localhost:5432/your_database --disable-model-prefix-protection

2023-07-15 10:43:45 - INFO - PostGres connection is open.
2023-07-15 10:43:46 - INFO - PostGres connection is closed.
2023-07-15 10:43:46 - INFO - Generating models...
2023-07-15 10:43:48 - INFO - Models generated successfully: /path/to/your/project/models.py
2023-07-15 10:43:48 - INFO - File formatted successfully: /path/to/your/project/models.py
```

This will generate models with direct "model_" prefixed fields:

```python title="Generated model with protection disabled"
class ModelTestItemsBaseSchema(CustomModel):
    """ModelTestItems Base Schema."""

    model_config = ConfigDict(protected_namespaces=())

    # Primary Keys
    id: int

    # Columns
    created_at: datetime.datetime | None = Field(default=None)
    model_id: UUID4 | None = Field(default=None)
    model_type: str | None = Field(default=None)
    model_version: str | None = Field(default=None)
    name: str
    updated_at: datetime.datetime | None = Field(default=None)
```

## Usage Differences

### With Default Behavior
When using the default models, you need to use the aliased field names:

```python title="Using models with default protection"
from models import ModelTestItemsBaseSchema

# Creating an instance
item = ModelTestItemsBaseSchema(
    id=1,
    name="Test Item",
    field_model_type="product",  # Use the prefixed field name
    field_model_version="v1.0",
    field_model_id="123e4567-e89b-12d3-a456-426614174000"
)

# But when serializing to JSON, the original column names are used
print(item.model_dump(by_alias=True))
# {'id': 1, 'name': 'Test Item', 'model_type': 'product', 'model_version': 'v1.0', 'model_id': '123e4567-e89b-12d3-a456-426614174000', ...}
```

### With Protection Disabled
With protection disabled, you can use the original column names directly:

```python title="Using models with protection disabled"
from models import ModelTestItemsBaseSchema

# Creating an instance
item = ModelTestItemsBaseSchema(
    id=1,
    name="Test Item",
    model_type="product",  # Use the original column name
    model_version="v1.0",
    model_id="123e4567-e89b-12d3-a456-426614174000"
)

# Serializing to JSON uses the same names
print(item.model_dump())
# {'id': 1, 'name': 'Test Item', 'model_type': 'product', 'model_version': 'v1.0', 'model_id': '123e4567-e89b-12d3-a456-426614174000', ...}
```

## When to Use This Option

Consider using this option when:

* You are working with machine learning models where fields like `model_id`, `model_version`, and `model_type` are common and meaningful
* You're building data science applications that need to track model lineage, versioning, and metadata
* You have automated processes that need field names to match database column names exactly
* You're using tools that don't handle aliases well
* You need to serialize/deserialize models with original field names
* You're integrating with external systems that expect specific field names

Keep the default behavior when:

* You want to adhere to Pydantic's recommended practices
* You need maximum compatibility with various Pydantic versions
* Your field naming can be flexible

## Clean Up

### Remove Test Database Objects

When done testing, you can clean up your database:

```sql title="model_prefix_cleanup.sql"
-- Cleanup script for testing model prefix protection feature

-- Drop the view first
DROP VIEW IF EXISTS model_test_items_view;

-- Drop the table and all dependent objects
DROP TABLE IF EXISTS model_test_items CASCADE;

-- If you created any additional objects, drop them here
-- DROP TYPE IF EXISTS your_custom_type;
-- DROP FUNCTION IF EXISTS your_custom_function();
```

To run this cleanup script:

```bash title="Run cleanup script"
$ psql -d your_database -f model_prefix_cleanup.sql

DROP VIEW
DROP TABLE
```

## References

These resources provide more information about Pydantic's protected namespaces feature and the reasoning behind it:

- [Pydantic Documentation: Protected Namespaces](https://docs.pydantic.dev/2.0/usage/model_config/#protected-namespaces) - Official documentation explaining Pydantic's protected namespaces feature and how to configure them.
- [Pydantic GitHub Issue #9427](https://github.com/pydantic/pydantic/issues/9427) - Discussion about the model_ prefix protection in Pydantic v2 and its impact on users migrating from v1.
