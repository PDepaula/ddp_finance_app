from sqlalchemy import select, insert, update, delete, join
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from app.models.schema import transactions, categories
from app.models.domain import Transaction, TransactionCreate, TransactionWithCategory

# Pure function to build a query for listing transactions
def list_transactions_query(
    limit: int = 100, 
    offset: int = 0,
    category_id: Optional[int] = None
):
    """Build a query for listing transactions with optional filtering"""
    query = (
        select(
            transactions, 
            categories.c.name.label('category_name'),
            categories.c.description.label('category_description')
        )
        .select_from(
            transactions.outerjoin(
                categories,
                transactions.c.category_id == categories.c.id
            )
        )
        .order_by(transactions.c.date.desc())
        .limit(limit)
        .offset(offset)
    )
    
    # Apply category filter if provided
    if category_id is not None:
        query = query.where(transactions.c.category_id == category_id)
        
    return query

# Pure function to build a query for getting a single transaction
def get_transaction_query(transaction_id: int):
    """Build a query to get a single transaction by ID"""
    return (
        select(
            transactions, 
            categories.c.name.label('category_name'),
            categories.c.description.label('category_description')
        )
        .select_from(
            transactions.outerjoin(
                categories,
                transactions.c.category_id == categories.c.id
            )
        )
        .where(transactions.c.id == transaction_id)
    )

# Pure function to build an insert statement for creating a transaction
def create_transaction_statement(transaction_data: TransactionCreate):
    """Build an insert statement for creating a transaction"""
    return (
        insert(transactions)
        .values(**transaction_data.dict())
        .returning(transactions)
    )

# Pure function to build an update statement for updating a transaction
def update_transaction_statement(transaction_id: int, transaction_data: Dict[str, Any]):
    """Build an update statement for updating a transaction"""
    return (
        update(transactions)
        .where(transactions.c.id == transaction_id)
        .values(**transaction_data)
        .returning(transactions)
    )

# Pure function to build a delete statement for deleting a transaction
def delete_transaction_statement(transaction_id: int):
    """Build a delete statement for deleting a transaction"""
    return (
        delete(transactions)
        .where(transactions.c.id == transaction_id)
    )

# Function to convert a row to a TransactionWithCategory model
def row_to_transaction_with_category(row) -> TransactionWithCategory:
    """Convert a database row to a TransactionWithCategory model"""
    # Extract transaction data
    transaction_data = {
        "id": row.id,
        "amount": row.amount,
        "description": row.description,
        "date": row.date,
        "category_id": row.category_id,
        "created_at": row.created_at,
    }
    
    # Create base transaction
    transaction = Transaction(**transaction_data)
    
    # Add category if available
    category_data = None
    if hasattr(row, 'category_name') and row.category_name:
        category_data = {
            "id": row.category_id,
            "name": row.category_name,
            "description": row.category_description,
            "created_at": row.created_at  # Approximate, as we don't have the actual category created_at
        }
    
    # Create TransactionWithCategory
    return TransactionWithCategory(
        **transaction.dict(),
        category=category_data
    )

# --- Handler functions that compose the above functions ---

async def list_transactions(
    db: AsyncSession,
    limit: int = 100,
    offset: int = 0,
    category_id: Optional[int] = None
) -> List[TransactionWithCategory]:
    """List transactions with optional filtering"""
    # Build query using pure function
    query = list_transactions_query(limit, offset, category_id)
    
    # Execute query (side effect)
    result = await db.execute(query)
    
    # Transform results using pure function
    return [row_to_transaction_with_category(row) for row in result]

async def get_transaction(
    db: AsyncSession,
    transaction_id: int
) -> Optional[TransactionWithCategory]:
    """Get a single transaction by ID"""
    # Build query using pure function
    query = get_transaction_query(transaction_id)
    
    # Execute query (side effect)
    result = await db.execute(query)
    row = result.first()
    
    # Return None if not found or transform using pure function
    return row_to_transaction_with_category(row) if row else None

async def create_transaction(
    db: AsyncSession,
    transaction_data: TransactionCreate
) -> Transaction:
    """Create a new transaction"""
    # Build statement using pure function
    stmt = create_transaction_statement(transaction_data)
    
    # Execute statement (side effect)
    result = await db.execute(stmt)
    
    # Get the created transaction
    transaction_row = result.first()
    
    # Convert to domain model and return
    return Transaction.from_orm(transaction_row)

async def update_transaction(
    db: AsyncSession,
    transaction_id: int,
    transaction_data: Dict[str, Any]
) -> Optional[Transaction]:
    """Update an existing transaction"""
    # Build statement using pure function
    stmt = update_transaction_statement(transaction_id, transaction_data)
    
    # Execute statement (side effect)
    result = await db.execute(stmt)
    
    # Get the updated transaction
    transaction_row = result.first()
    
    # Convert to domain model and return
    return Transaction.from_orm(transaction_row) if transaction_row else None

async def delete_transaction(
    db: AsyncSession,
    transaction_id: int
) -> bool:
    """Delete a transaction"""
    # Build statement using pure function
    stmt = delete_transaction_statement(transaction_id)
    
    # Execute statement (side effect)
    result = await db.execute(stmt)
    
    # Return whether deletion was successful
    return result.rowcount > 0