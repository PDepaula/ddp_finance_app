from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.models.schema import categories, transactions
from app.models.domain import Category, CategoryCreate

# Pure function to build a query for listing categories
def list_categories_query(limit: int = 100, offset: int = 0):
    """Build a query for listing categories"""
    return (
        select(categories)
        .order_by(categories.c.name)
        .limit(limit)
        .offset(offset)
    )

# Pure function to build a query for getting a single category
def get_category_query(category_id: int):
    """Build a query to get a single category by ID"""
    return (
        select(categories)
        .where(categories.c.id == category_id)
    )

# Pure function to build a query for getting categories with transaction counts
def list_categories_with_counts_query():
    """Build a query for listing categories with transaction counts"""
    count_subq = (
        select(
            transactions.c.category_id,
            func.count().label('transaction_count')
        )
        .group_by(transactions.c.category_id)
        .alias('count_subq')
    )
    
    return (
        select(
            categories,
            func.coalesce(count_subq.c.transaction_count, 0).label('transaction_count')
        )
        .outerjoin(
            count_subq,
            categories.c.id == count_subq.c.category_id
        )
        .order_by(categories.c.name)
    )

# Pure function to build an insert statement for creating a category
def create_category_statement(category_data: CategoryCreate):
    """Build an insert statement for creating a category"""
    return (
        insert(categories)
        .values(**category_data.dict())
        .returning(categories)
    )

# Pure function to build an update statement for updating a category
def update_category_statement(category_id: int, category_data: Dict[str, Any]):
    """Build an update statement for updating a category"""
    return (
        update(categories)
        .where(categories.c.id == category_id)
        .values(**category_data)
        .returning(categories)
    )

# Pure function to build a delete statement for deleting a category
def delete_category_statement(category_id: int):
    """Build a delete statement for deleting a category"""
    return (
        delete(categories)
        .where(categories.c.id == category_id)
    )

# --- Handler functions that compose the above functions ---

async def list_categories(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0
) -> List[Category]:
    """List categories"""
    # Build query using pure function
    query = list_categories_query(limit, offset)
    
    # Execute query (side effect)
    result = await db.execute(query)
    
    # Transform results
    return [Category.from_orm(row) for row in result]

async def get_category(
    db: AsyncSession,
    category_id: int
) -> Optional[Category]:
    """Get a single category by ID"""
    # Build query using pure function
    query = get_category_query(category_id)
    
    # Execute query (side effect)
    result = await db.execute(query)
    row = result.first()
    
    # Return None if not found or transform
    return Category.from_orm(row) if row else None

async def list_categories_with_counts(db: AsyncSession) -> List[Dict[str, Any]]:
    """List categories with transaction counts"""
    # Build query using pure function
    query = list_categories_with_counts_query()
    
    # Execute query (side effect)
    result = await db.execute(query)
    
    # Transform results
    return [
        {
            **Category.from_orm(row).dict(),
            "transaction_count": row.transaction_count
        }
        for row in result
    ]

async def create_category(
    db: AsyncSession,
    category_data: CategoryCreate
) -> Category:
    """Create a new category"""
    # Build statement using pure function
    stmt = create_category_statement(category_data)
    
    # Execute statement (side effect)
    result = await db.execute(stmt)
    
    # Get the created category
    category_row = result.first()
    
    # Convert to domain model and return
    return Category.from_orm(category_row)

async def update_category(
    db: AsyncSession,
    category_id: int,
    category_data: Dict[str, Any]
) -> Optional[Category]:
    """Update an existing category"""
    # Build statement using pure function
    stmt = update_category_statement(category_id, category_data)
    
    # Execute statement (side effect)
    result = await db.execute(stmt)
    
    # Get the updated category
    category_row = result.first()
    
    # Convert to domain model and return
    return Category.from_orm(category_row) if category_row else None

async def delete_category(
    db: AsyncSession,
    category_id: int
) -> bool:
    """Delete a category"""
    # Build statement using pure function
    stmt = delete_category_statement(category_id)
    
    # Execute statement (side effect)
    result = await db.execute(stmt)
    
    # Return whether deletion was successful
    return result.rowcount > 0