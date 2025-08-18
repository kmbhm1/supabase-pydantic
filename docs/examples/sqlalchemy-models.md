# Working with SQLAlchemy Models

This guide demonstrates how to generate and use SQLAlchemy models with `supabase-pydantic`. The SQLAlchemy generator creates comprehensive ORM models that include Insert and Update variants for better type safety and validation.

## Prerequisites

You will need to have:

- Python 3.10 or higher
- A Supabase project or PostgreSQL database
- The `supabase-pydantic` package installed

## Generating SQLAlchemy Models

To generate SQLAlchemy models from your database:

```bash
$ sb-pydantic gen --type sqlalchemy --local
```

Or with a database URL:

```bash
$ sb-pydantic gen --type sqlalchemy --db-url postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

### Customizing Output

You can customize the output directory and specify schemas:

```bash
$ sb-pydantic gen --type sqlalchemy --local --dir ./my_models --schema public --schema auth
```

## Generated Model Structure

The SQLAlchemy generator creates three types of models for each table:

1. **Base Models**: Complete table representation
2. **Insert Models**: For creating new records
3. **Update Models**: For modifying existing records

### Example Output

For a table like `users`:

```python
from __future__ import annotations
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Declarative Base Class."""
    pass

class User(Base):
    """User base class."""
    
    # Class for table: users
    
    # Primary Keys
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    # Columns
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String)
    organization_id: Mapped[UUID4] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    
    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="users")
    
    # Table Args
    __table_args__ = (
        { 'schema': 'public' }
    )

class UserInsert(Base):
    """User Insert model."""
    
    # Use this model for inserting new records into users table.
    # Auto-generated and identity fields are excluded.
    # Fields with defaults are optional.
    # Primary key field(s): id
    # Required fields: id, name, organization_id
    
    # Primary Keys
    id: Mapped[int] = mapped_column(Integer)
    
    # Columns
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String)
    organization_id: Mapped[UUID4] = mapped_column(UUID(as_uuid=True))
    
    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="users")

class UserUpdate(Base):
    """User Update model."""
    
    # Use this model for updating existing records in users table.
    # All fields are optional to support partial updates.
    # Primary key field(s) should be used to identify records: id
    
    # Primary Keys
    id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Columns
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    organization_id: Mapped[UUID4 | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    
    # Relationships
    organization: Mapped[Organization | None] = relationship("Organization", back_populates="users")
```

## Key Features

### 1. Base Models

- Complete representation of table structure
- Proper handling of primary keys
- Relationship definitions with back-populates
- Table arguments including schema

### 2. Insert Models

- Designed for creating new records
- Required fields remain required
- Auto-generated fields are optional
- Clear documentation about primary keys and required fields

### 3. Update Models

- All fields are optional to support partial updates
- Primary key fields are included but nullable
- Maintains relationship definitions
- Optimized for PATCH/PUT operations

## Using SQLAlchemy Models with FastAPI

Here's an example of using these models with FastAPI and SQLAlchemy:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from .models import User, UserInsert, UserUpdate
from .database import get_db

app = FastAPI()

@app.post("/users/", response_model=User)
async def create_user(user: UserInsert, db: AsyncSession = Depends(get_db)):
    db_user = User(
        name=user.name,
        email=user.email,
        organization_id=user.organization_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.patch("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        if value is not None:  # Only update provided fields
            setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
```

## Best Practices

1. **Use Type-Specific Models**:
   - Use base models for queries and responses
   - Use Insert models for creation operations
   - Use Update models for modification operations

2. **Partial Updates**:
   - Use `model_dump(exclude_unset=True)` to only include fields that were explicitly set
   - Only update non-None values to preserve existing data

3. **Relationship Handling**:
   - Consider using dedicated endpoints for managing relationships
   - Be careful with cascading operations

4. **Database Migrations**:
   - Use Alembic for schema migrations
   - Keep generated models in sync with your database schema

## Advanced Usage

### Custom Validation

You can extend the generated models with custom validation:

```python
from sqlalchemy.orm import validates

class User(Base):
    # ... existing code ...
    
    @validates('email')
    def validate_email(self, key, email):
        if email and '@' not in email:
            raise ValueError("Invalid email format")
        return email
```

### Adding Business Logic

Extend the models with business logic methods:

```python
class User(Base):
    # ... existing code ...
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
```

## Conclusion

The SQLAlchemy model generator in `supabase-pydantic` provides a comprehensive solution for interacting with your database using modern SQLAlchemy features. The specialized Insert and Update models ensure type safety while maintaining flexibility for different database operations.
