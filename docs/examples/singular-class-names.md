# Singular Class Names

By default, supabase-pydantic generates class names that directly mirror your table names. For tables with plural names like `products`, `users`, or `categories`, this results in class names like `Products`, `Users`, and `Categories`.

However, following object-oriented programming best practices, many developers prefer singular class names that represent individual entities. A `Product` class represents a single product, not multiple products.

The `--singular-names` flag addresses this preference by automatically converting plural table names to singular class names.

## Understanding the Generated Class Structure

supabase-pydantic generates two types of classes for each table:

1. **Base Schema Classes** (e.g., `ProductBaseSchema`): Parent classes containing only the direct table column definitions
2. **Main Model Classes** (e.g., `Product`): The classes you actually use in your code, which inherit from the base schemas and include relationship fields

The `--singular-names` flag affects **both** the base schema names and the main model class names.

## Basic Usage

### Default Behavior (Plural Class Names)

```bash
supabase-pydantic gen --db-url "postgresql://user:pass@localhost/mydb"
```

For a table named `products`, this generates:

```python
# Base schema (parent class)
class ProductsBaseSchema(BaseModel):
    id: int
    name: str
    price: Decimal
    # ... other fields

# Main model class (inherits from base schema)
class Products(ProductsBaseSchema):
    pass

# CRUD model variants
class ProductsInsert(BaseModelInsert):
    name: str
    price: Decimal
    # ... other fields

class ProductsUpdate(BaseModelUpdate):
    name: str | None = None
    price: Decimal | None = None
    # ... other fields
```

### With Singular Class Names

```bash
supabase-pydantic gen --db-url "postgresql://user:pass@localhost/mydb" --singular-names
```

For the same `products` table, this generates:

```python
# Base schema (parent class) - now singular
class ProductBaseSchema(BaseModel):  # Note: "Product" not "Products"
    id: int
    name: str
    price: Decimal
    # ... other fields

# Main model class (inherits from base schema) - singular
class Product(ProductBaseSchema):  # Note: "Product" not "Products"
    pass

# CRUD model variants - also singular
class ProductInsert(BaseModelInsert):
    name: str
    price: Decimal
    # ... other fields

class ProductUpdate(BaseModelUpdate):
    name: str | None = None
    price: Decimal | None = None
    # ... other fields
```

## Examples

### Common Table Name Transformations

| Table Name | Default Class Name | With `--singular-names` |
|------------|-------------------|-------------------------|
| `products` | `Products` | `Product` |
| `users` | `Users` | `User` |
| `categories` | `Categories` | `Category` |
| `companies` | `Companies` | `Company` |
| `addresses` | `Addresses` | `Address` |
| `order_items` | `OrderItems` | `OrderItem` |
| `user_profiles` | `UserProfiles` | `UserProfile` |

### Complete Example

Let's say you have a database with these tables:
- `users`
- `products` 
- `orders`
- `order_items`

#### Without `--singular-names`:

```python
# Base schemas (parent classes)
class UsersBaseSchema(BaseModel):
    id: int
    email: str
    name: str

class ProductsBaseSchema(BaseModel):
    id: int
    name: str
    price: Decimal

class OrdersBaseSchema(BaseModel):
    id: int
    user_id: int
    total: Decimal

class OrderItemsBaseSchema(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int

# Main model classes (inherit from base schemas)
class Users(UsersBaseSchema):
    pass

class Products(ProductsBaseSchema):
    pass

class Orders(OrdersBaseSchema):
    pass

class OrderItems(OrderItemsBaseSchema):
    pass
```

#### With `--singular-names`:

```python
# Base schemas (parent classes) - now singular
class UserBaseSchema(BaseModel):
    id: int
    email: str
    name: str

class ProductBaseSchema(BaseModel):
    id: int
    name: str
    price: Decimal

class OrderBaseSchema(BaseModel):
    id: int
    user_id: int
    total: Decimal

class OrderItemBaseSchema(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int

# Main model classes (inherit from base schemas) - singular
class User(UserBaseSchema):
    pass

class Product(ProductBaseSchema):
    pass

class Order(OrderBaseSchema):
    pass

class OrderItem(OrderItemBaseSchema):
    pass
```

## When to Use Singular Names

### ✅ Recommended Use Cases

- **Following OOP best practices**: Individual class instances represent single entities
- **API development**: RESTful APIs typically use singular nouns for resource models
- **Code readability**: `user = User()` reads more naturally than `user = Users()`
- **Framework conventions**: Many ORMs and frameworks expect singular model names
- **Team standards**: When your team prefers singular class names

### ⚠️ Consider Carefully

- **Existing codebases**: Changing from plural to singular names is a breaking change
- **Database naming conventions**: If your database uses singular table names, you may not need this flag
- **Mixed naming**: If some tables are singular and others plural, results may be inconsistent

## Important Notes

### What Gets Singularized

The `--singular-names` flag **only affects class names**. It does not change:

- ❌ **Table names**: Still references the actual `products` table
- ❌ **Column names**: Field names remain unchanged
- ❌ **Relationship field names**: Foreign key relationships use appropriate pluralization

### Relationship Handling

The singularization is intelligent about relationships and follows semantic conventions for relationship field names:

```python
# With --singular-names enabled - Base schemas (parent classes, table columns only)
class UserBaseSchema(BaseModel):
    id: int
    email: str

class OrderBaseSchema(BaseModel):
    id: int
    user_id: int

# Main model classes (inherit from base schemas, include relationships)
class User(UserBaseSchema):
    # One-to-many relationship: user has many orders (plural)
    orders: list[Order] | None = Field(default=None)

class Order(OrderBaseSchema):
    # Many-to-one relationship: order belongs to one user (singular)
    user: User | None = Field(default=None)
```

#### Semantic Pluralization Rules for Relationships

The `--singular-names` flag **only affects class names**, not relationship field names. Relationship fields follow semantic grammar rules based on the relationship type:

| Relationship Type | Field Name Convention | Example | Reasoning |
|------------------|----------------------|---------|-----------|
| **One-to-One** | Singular | `user.profile` | One user has one profile |
| **One-to-Many** | Plural | `user.orders` | One user has many orders |
| **Many-to-One** | Singular | `order.user` | Many orders belong to one user |
| **Many-to-Many** | Plural | `post.tags` | One post has many tags |

#### Detailed Examples

Consider a database with `users`, `orders`, `products`, and `order_items` tables:

```python
# Generated with --singular-names - Base schemas (parent classes, table columns only)
class UserBaseSchema(BaseModel):
    id: int
    email: str
    name: str

class OrderBaseSchema(BaseModel):
    id: int
    user_id: int
    total: Decimal

class ProductBaseSchema(BaseModel):
    id: int
    name: str
    price: Decimal

class OrderItemBaseSchema(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int

class UserProfileBaseSchema(BaseModel):
    id: int
    user_id: int
    bio: str
    avatar_url: str | None = None

class CategoryBaseSchema(BaseModel):
    id: int
    name: str
    description: str | None = None

# Main model classes (inherit from base schemas, include relationships)
class User(UserBaseSchema):
    # One-to-many: A user can have multiple orders
    orders: list[Order] | None = Field(default=None)
    
    # One-to-one: A user has one profile (if profile table exists)
    profile: UserProfile | None = Field(default=None)

class Order(OrderBaseSchema):
    # Many-to-one: Each order belongs to one user
    user: User | None = Field(default=None)
    
    # One-to-many: An order can have multiple items
    order_items: list[OrderItem] | None = Field(default=None)

class Product(ProductBaseSchema):
    # One-to-many: A product can be in multiple order items
    order_items: list[OrderItem] | None = Field(default=None)
    
    # Many-to-many: A product can have multiple categories
    categories: list[Category] | None = Field(default=None)

class OrderItem(OrderItemBaseSchema):
    # Many-to-one: Each item belongs to one order
    order: Order | None = Field(default=None)
    
    # Many-to-one: Each item is for one product
    product: Product | None = Field(default=None)

class UserProfile(UserProfileBaseSchema):
    # One-to-one: Profile belongs to one user
    user: User | None = Field(default=None)

class Category(CategoryBaseSchema):
    # Many-to-many: A category can have multiple products
    products: list[Product] | None = Field(default=None)
```

#### Why This Approach?

1. **Natural Language**: Field names read like natural English
   - ✅ `user.orders` (user has orders)
   - ❌ `user.order` (doesn't make semantic sense for collections)

2. **Developer Expectations**: Follows common ORM conventions
   - Plural fields suggest collections/arrays
   - Singular fields suggest single objects

3. **Type Safety**: Field names match their type hints
   - `orders: list[Order]` (plural name, list type)
   - `user: User` (singular name, single object type)

4. **Database Relationships**: Reflects actual database cardinality
   - One-to-many foreign keys naturally create collections
   - Many-to-one foreign keys reference single entities

### Backward Compatibility

The `--singular-names` flag is completely optional and defaults to `False`, ensuring:

- **No breaking changes** for existing users
- **Explicit opt-in** behavior
- **Consistent results** when not specified

## Advanced Usage

### Combining with Other Options

```bash
# Generate singular names with SQLAlchemy models
supabase-pydantic gen \
  --db-url "postgresql://user:pass@localhost/mydb" \
  --singular-names \
  --type sqlalchemy

# Generate singular names for specific schemas
supabase-pydantic gen \
  --db-url "postgresql://user:pass@localhost/mydb" \
  --singular-names \
  --schema public \
  --schema api

# Generate singular names without CRUD models
supabase-pydantic gen \
  --db-url "postgresql://user:pass@localhost/mydb" \
  --singular-names \
  --no-crud-models
```

## Best Practices

### 1. Be Consistent

Choose either singular or plural class names for your entire project. Mixing both can be confusing.

### 2. Consider Your Team

Make sure your team agrees on the naming convention before implementing it across your codebase.

### 3. Update Documentation

If you switch to singular names, update your API documentation and code comments accordingly.

### 4. Test Thoroughly

When migrating existing code to use singular names, ensure all references are updated and tests pass.

## Troubleshooting

### Irregular Plurals

The singularization uses the `inflection` library, which handles most English pluralization rules correctly:

- `categories` → `category`
- `companies` → `company`  
- `people` → `person`
- `children` → `child`

### Edge Cases

For unusual table names or non-English words, the singularization might not work as expected. In such cases, consider:

1. Renaming the table if possible
2. Using the default plural class names
3. Manually editing the generated code (though this isn't recommended for maintainability)

### Mixed Naming Conventions

If your database has both singular and plural table names, the `--singular-names` flag will attempt to singularize all names, which might result in some odd transformations for already-singular tables.

## Migration Guide

If you're migrating from plural to singular class names:

1. **Generate new models** with `--singular-names`
2. **Update all imports** in your codebase
3. **Update type hints** and variable declarations
4. **Run your test suite** to catch any missed references
5. **Update API documentation** if applicable

Remember: This is a breaking change that will require code updates throughout your application.
