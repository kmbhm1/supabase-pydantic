# Working with Insert and Update Models

This guide demonstrates how to work with the automatically generated Insert and Update models in `supabase-pydantic`. These models are specifically designed to handle the different requirements for inserting new records and updating existing ones in your Supabase database.

!!! note "Alignment with Supabase TypeScript Types"
    This feature aligns with Supabase's TypeScript type generation, which generates three types for each table:
    `Database['public']['Tables']['table_name']['Row']` for complete rows,
    `Database['public']['Tables']['table_name']['Insert']` for insertions, and
    `Database['public']['Tables']['table_name']['Update']` for updates.
    See the [Supabase TypeScript Type Generator](https://supabase.com/docs/reference/javascript/typescript-support) for more details.
    
    By following this pattern, we ensure consistency across your full-stack application, whether you're working with TypeScript on the frontend or Python on the backend.

## Prerequisites and Setup

You will need to follow the [prerequisites](/supabase-pydantic/examples/setup-slack-simple-fastapi/#prerequisites) listed in the original example.

## New Generated Classes

When you run the schema generation command (`sb-pydantic gen`), three model classes are generated for each table in your database:

1. **Base (Row) Model** (e.g., `ProductBaseSchema`/`Product`)
    - Contains all fields with their proper types
    - Used primarily for responses and full object representation

2. **Insert Model** (e.g., `ProductInsert`)
    - Includes only the fields required for creating new records
    - Makes auto-generated or defaulted fields like `id` and `inserted_at` optional
    - Required fields remain required, optional fields are still optional

3. **Update Model** (e.g., `ProductUpdate`)
    - Makes all fields optional since updates typically only modify a subset of fields
    - Uses `Optional` types to ensure type safety when updating

## Understanding Insert and Update Models

When working with databases, the fields required for creating a new record (insertion) often differ from those needed to update an existing record. `supabase-pydantic` automatically generates specialized models for these operations:

- **Insert Models**: Include all required fields for creating new records
- **Update Models**: Make all fields optional since you typically only update specific fields

## Example Schema

Let's look at a more comprehensive example using an e-commerce product catalog schema:

```sql
create type product_status as enum ('draft', 'active', 'archived');
create type inventory_status as enum ('in_stock', 'low_stock', 'out_of_stock');

create table products (
    id uuid default gen_random_uuid() primary key,
    sku text not null unique,
    name text not null,
    description text,
    price decimal(10,2) not null,
    category_id uuid references categories(id),
    brand_id uuid references brands(id),
    created_by uuid references auth.users,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now()),
    published_at timestamp with time zone,
    status product_status default 'draft',
    inventory_status inventory_status default 'out_of_stock',
    stock_quantity integer default 0,
    weight_grams integer,
    dimensions jsonb default '{"length": 0, "width": 0, "height": 0}',
    tags text[] default '{}',
    attributes jsonb default '{}'
);
```

## Generated Models

For the above schema, `supabase-pydantic` will generate three model classes with detailed field information (BaseSchema not included; see [previous tutorial](/supabase-pydantic/examples/setup-slack-simple-fastapi/#generating-schemas)):

```python
from datetime import datetime
from typing import Optional, List
from uuid import UUID4
from decimal import Decimal
from pydantic import BaseModel, Field, Json

# ... other definitions ...

class ProductsInsert(CustomModelInsert):
    """Products Insert Schema."""

    # Primary Keys
    id: UUID4 | None = Field(default=None)  # has default value

    # Field properties:
    # brand_id: nullable
    # category_id: nullable
    # created_at: has default value
    # created_by: nullable
    # description: nullable
    # dimensions: has default value
    # inventory_status: has default value
    # published_at: nullable
    # status: has default value
    # stock_quantity: has default value
    # tags: has default value
    # weight_grams: nullable

    # Required fields
    sku: str
    name: str
    price: Decimal

    # Optional fields
    brand_id: UUID4 | None = Field(default=None)
    category_id: UUID4 | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    created_by: UUID4 | None = Field(default=None)
    description: str | None = Field(default=None)
    dimensions: dict | Json | None = Field(default=None)
    inventory_status: str | None = Field(default=None)
    published_at: datetime | None = Field(default=None)
    status: str | None = Field(default=None)
    stock_quantity: int | None = Field(default=None)
    tags: list[str] | None = Field(default=None)
    weight_grams: int | None = Field(default=None)
    attributes: dict | Json | None = Field(default=None)


class ProductsUpdate(CustomModelUpdate):
    """Products Update Schema."""

    # Primary Keys
    id: UUID4 | None = Field(default=None)

    # Field properties (same as Insert)
    # brand_id: nullable
    # category_id: nullable
    # ...

    # All fields are optional in Update model
    brand_id: UUID4 | None = Field(default=None)
    category_id: UUID4 | None = Field(default=None)
    created_at: datetime | None = Field(default=None)
    created_by: UUID4 | None = Field(default=None)
    description: str | None = Field(default=None)
    dimensions: dict | Json | None = Field(default=None)
    inventory_status: str | None = Field(default=None)
    name: str | None = Field(default=None)
    price: Decimal | None = Field(default=None)
    published_at: datetime | None = Field(default=None)
    sku: str | None = Field(default=None)
    status: str | None = Field(default=None)
    stock_quantity: int | None = Field(default=None)
    tags: List[str] | None = Field(default=None)
    weight_grams: int | None = Field(default=None)
    attributes: dict | Json | None = Field(default=None)
```

### Key Features Illustrated

1. **Smart Field Analysis**:
    - Required fields are preserved in the Insert model (`sku`, `name`, `price`)
    - Fields with database defaults are optional (`id`, `created_at`, `stock_quantity`, etc.)
    - Nullable fields (like `description`, `weight_grams`) are properly typed with `| None`

2. **Advanced PostgreSQL Types**:
    - Enum types (`product_status`, `inventory_status`) are handled appropriately
    - Array types (`tags text[]`) are mapped to `list[str]`
    - JSONB fields (`dimensions`, `attributes`) support both `dict` and `Json` types
    - Decimal fields (`price`) use Python's `Decimal` for precision

3. **Field Property Documentation**:
    - Each model includes detailed comments about field properties
    - Clearly indicates which fields are nullable or have default values
    - Documents complex field relationships (foreign keys to `categories`, `brands`)

4. **Type Safety and Validation**:
    - Foreign keys use `UUID4` type for proper validation
    - Complex types are properly mapped (`jsonb` → `dict | Json`, `text[]` → `list[str]`)
    - All fields in Update model are optional with `| None`
    - Maintains type consistency with database constraints

5. **Default Value Handling**:\
    - Smart handling of PostgreSQL defaults (`default gen_random_uuid()`, `default '{}'`)
    - All optional fields use `Field(default=None)` for proper Pydantic validation
    - Preserves database-level default values while ensuring type safety

## Using the Models

Here's how to use these models in your FastAPI application:

```python
from fastapi import FastAPI, HTTPException
from supabase import create_client
from uuid import UUID4
from typing import list

app = FastAPI()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.post("/products/", response_model=Product)
async def create_product(product: ProductsInsert):
    # Validate and insert new product
    result = supabase.table("products").insert(product.model_dump()).execute()
    return result.data[0]

@app.patch("/products/{product_id}", response_model=Product)
async def update_product(product_id: UUID4, product: ProductsUpdate):
    # Only send non-None values for update
    update_data = {k: v for k, v in product.model_dump().items() if v is not None}
    result = supabase.table("products").update(update_data).eq("id", product_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return result.data[0]

@app.post("/products/{product_id}/stock", response_model=Product)
async def update_stock(product_id: UUID4, quantity: int):
    # Example of partial update using ProductsUpdate
    update = ProductsUpdate(stock_quantity=quantity)
    if quantity == 0:
        update.inventory_status = "out_of_stock"
    elif quantity < 10:
        update.inventory_status = "low_stock"
    else:
        update.inventory_status = "in_stock"
    
    result = supabase.table("products").update(update.model_dump(exclude_none=True)) \
        .eq("id", product_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return result.data[0]
```

## Key Features

1. **Smart Schema Handling**:
    - Insert models preserve required fields (`sku`, `name`, `price`)
    - Update models make all fields optional for partial updates
    - Proper handling of PostgreSQL types (enums, arrays, JSONB)

2. **Type Safety**:
    - Precise decimal handling for prices
    - Proper UUID handling for IDs and foreign keys
    - Array support for tags with `list[str]`
    - JSONB support for flexible attributes and dimensions

3. **Validation**:
    - Automatic validation of required fields
    - Enum validation for product and inventory status
    - Custom validators can be added for business logic

## Best Practices

1. **Use Specific Models for Specific Operations**:
    - Use `ProductsInsert` for creating new products
    - Use `ProductsUpdate` for modifying existing products
    - Use the base `Product` model for responses
    - Create specific endpoints for common operations (like stock updates)

2. **Handle Complex Updates**:
    - Use `model_dump(exclude_none=True)` to only send changed fields
    - Group related field updates (like stock quantity and status)
    - Consider business logic when updating related fields

3. **Error Handling**:
    - Validate business rules before database operations
    - Handle unique constraint violations (e.g., duplicate SKUs)
    - Provide clear error messages for validation failures

## Relationship Handling

The models handle relationships with other tables appropriately:

```python
class ProductWithRelations(Product):
    # One-to-One relationship
    primary_image: ProductImage | None
    
    # One-to-Many relationships
    variants: list[ProductVariant] | None
    reviews: list[ProductReview] | None
    
    # Many-to-Many relationships
    categories: list[Category] | None
    tags: list[Tag] | None
```

When working with relationships:

1. **Foreign Keys**:
    - `category_id` and `brand_id` are typed as `UUID4 | None`
    - Allows for optional relationships while maintaining type safety

2. **Nested Operations**:
    - Consider using separate endpoints for managing relationships
    - Handle cascading updates carefully (e.g., updating all variants)

3. **Data Loading**:
    - Use `.select('*')` for basic queries
    - Use `.select('*, categories(*)')` to include related data


## Conclusion

Using the generated Insert and Update models provides a type-safe and efficient way to handle database operations in your Supabase application. These models ensure that your API endpoints handle data correctly while maintaining proper validation and type checking.
