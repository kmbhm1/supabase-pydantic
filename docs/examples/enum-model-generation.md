# Generating Pydantic Models with Cross-Schema Enums

This guide demonstrates how to use `sb-pydantic` to generate Pydantic models with proper enum support when enums are defined in one schema but used in views from another schema. This is a common pattern where you have your core data tables in the `public` schema but expose API views in a separate `api` schema.

---

## Overview

In this example, we'll create:
- **Enums and tables** in the `public` schema
- **Views** in the `api` schema that reference the enums from `public`
- **Pydantic models** generated from the `api` schema that properly use the cross-schema enums

---

## Step 1: Database Setup Script

Run this SQL script to set up the test database structure:

```sql
-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS api;

-- Create enum types in the public schema
CREATE TYPE public.order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE public.user_role AS ENUM ('admin', 'user', 'moderator');

-- Create tables in the public schema
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role public.user_role DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id),
    status public.order_status DEFAULT 'pending',
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert some test data
INSERT INTO public.users (name, email, role) VALUES 
    ('John Doe', 'john@example.com', 'user'),
    ('Jane Admin', 'jane@example.com', 'admin'),
    ('Bob Moderator', 'bob@example.com', 'moderator');

INSERT INTO public.orders (user_id, status, total_amount) VALUES 
    (1, 'pending', 99.99),
    (1, 'processing', 149.50),
    (2, 'shipped', 299.00),
    (3, 'delivered', 75.25);

-- Create views in the api schema that use the enums from public schema
CREATE VIEW api.user_profiles AS
SELECT 
    id,
    name,
    email,
    role,  -- This uses public.user_role enum
    created_at
FROM public.users;

CREATE VIEW api.order_summary AS
SELECT 
    o.id,
    o.status,  -- This uses public.order_status enum
    o.total_amount,
    u.name as customer_name,
    u.email as customer_email,
    o.created_at
FROM public.orders o
JOIN public.users u ON o.user_id = u.id;

-- Create a view with array of enums to test array handling
CREATE VIEW api.order_status_options AS
SELECT 
    ARRAY['pending', 'processing', 'shipped', 'delivered', 'cancelled']::public.order_status[] as available_statuses,
    'Order Status Options' as description;
```

---

```bash
sb-pydantic gen --type pydantic --framework fastapi --local --schema public --schema api
```

This command generates models for both the `public` and `api` schemas, allowing the cross-schema enum references to be properly resolved.

---

## Step 3: Generated Output

The command will generate a file `schema_api_latest.py` that includes:

### Enum Classes
Notice how the enums are prefixed with their schema name:

```python
class PublicOrderStatusEnum(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class PublicUserRoleEnum(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'
```

### Model Classes with Cross-Schema Enums
The views from the `api` schema properly reference enums from the `public` schema:

```python
class UserProfilesBaseSchema(CustomModel):
    """UserProfiles Base Schema."""
    
    created_at: datetime.datetime | None = Field(default=None)
    email: str | None = Field(default=None)
    id: int | None = Field(default=None)
    name: str | None = Field(default=None)
    role: PublicUserRoleEnum | None = Field(default=None)  # Cross-schema enum!

class OrderSummaryBaseSchema(CustomModel):
    """OrderSummary Base Schema."""
    
    created_at: datetime.datetime | None = Field(default=None)
    customer_email: str | None = Field(default=None)
    customer_name: str | None = Field(default=None)
    id: int | None = Field(default=None)
    status: PublicOrderStatusEnum | None = Field(default=None)  # Cross-schema enum!
    total_amount: Decimal | None = Field(default=None)

class OrderStatusOptionsBaseSchema(CustomModel):
    """OrderStatusOptions Base Schema."""
    
    available_statuses: list[PublicOrderStatusEnum] | None = Field(default=None)  # Array of enums!
    description: str | None = Field(default=None)
```

---

## Step 4: Key Features Demonstrated

This example showcases several important features:

1. **Cross-Schema Enum Discovery**: Enums defined in `public` are properly detected and used in `api` views
2. **Schema-Prefixed Naming**: Enum classes are named `PublicOrderStatusEnum` to indicate their origin schema
3. **Array Support**: The `available_statuses` field shows proper handling of enum arrays
4. **View Support**: Database views are treated the same as tables for model generation

---

## Step 5: Cleanup Script

When you're done testing, run this cleanup script:

```sql
-- Drop views in the api schema
DROP VIEW IF EXISTS api.order_status_options;
DROP VIEW IF EXISTS api.order_summary;
DROP VIEW IF EXISTS api.user_profiles;

-- Drop tables in the public schema (this will cascade to dependent objects)
DROP TABLE IF EXISTS public.orders CASCADE;
DROP TABLE IF EXISTS public.users CASCADE;

-- Drop enum types in the public schema
DROP TYPE IF EXISTS public.order_status CASCADE;
DROP TYPE IF EXISTS public.user_role CASCADE;

-- Drop the api schema (if it was created just for testing)
DROP SCHEMA IF EXISTS api CASCADE;
```

---

## Notes

- **Schema Prefixing**: Notice how enum classes are prefixed with their origin schema (`PublicOrderStatusEnum`) to avoid naming conflicts
- **Cross-Schema References**: Views in the `api` schema can seamlessly use enums defined in the `public` schema
- **Array Handling**: Enum arrays are properly typed as `list[EnumType]`
- **Backward Compatibility**: This feature works alongside existing single-schema setups without any breaking changes

This cross-schema enum support makes it easy to maintain clean separation between your data layer (`public`) and API layer (`api`) while still getting full type safety in your Pydantic models.
