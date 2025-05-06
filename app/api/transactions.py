from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.core.templates import templates
from app.db import get_db
from app.models.domain import TransactionCreate, Transaction, TransactionWithCategory
from app.queries import transactions as transaction_queries
from app.queries import categories as category_queries

router = APIRouter()

# --- API Routes (for JSON responses) ---

@router.get("/api/transactions/", response_model=List[TransactionWithCategory])
async def api_list_transactions(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    category_id: Optional[int] = None
):
    """List transactions with optional filtering"""
    return await transaction_queries.list_transactions(db, limit, offset, category_id)

@router.get("/api/transactions/{transaction_id}", response_model=TransactionWithCategory)
async def api_get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a transaction by ID"""
    transaction = await transaction_queries.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/api/transactions/", response_model=Transaction)
async def api_create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction"""
    return await transaction_queries.create_transaction(db, transaction_data)

@router.put("/api/transactions/{transaction_id}", response_model=Transaction)
async def api_update_transaction(
    transaction_id: int,
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a transaction"""
    transaction = await transaction_queries.update_transaction(
        db, transaction_id, transaction_data.dict()
    )
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/api/transactions/{transaction_id}")
async def api_delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a transaction"""
    success = await transaction_queries.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

# --- HTML Routes (for HTMX interactions) ---

@router.get("/transactions/", response_class=HTMLResponse)
async def list_transactions_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    category_id: Optional[int] = None
):
    """Render the transactions list page"""
    transactions = await transaction_queries.list_transactions(
        db, category_id=category_id
    )
    categories = await category_queries.list_categories(db)
    
    return templates.TemplateResponse(
        "transactions/list.html",
        {
            "request": request,
            "transactions": transactions,
            "categories": categories,
            "selected_category_id": category_id
        }
    )

@router.get("/transactions/new", response_class=HTMLResponse)
async def new_transaction_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Render the new transaction form"""
    categories = await category_queries.list_categories(db)
    
    return templates.TemplateResponse(
        "transactions/create.html",
        {
            "request": request,
            "categories": categories
        }
    )

@router.post("/transactions/", response_class=HTMLResponse)
async def create_transaction_form(
    request: Request,
    amount: float = Form(...),
    description: Optional[str] = Form(None),
    date: str = Form(...),
    category_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a transaction from form data and return partial HTML"""
    # Parse date string
    transaction_date = datetime.fromisoformat(date)
    
    # Create transaction data
    transaction_data = TransactionCreate(
        amount=amount,
        description=description,
        date=transaction_date,
        category_id=category_id if category_id else None
    )
    
    # Save to database
    await transaction_queries.create_transaction(db, transaction_data)
    
    # Redirect to list view using HX-Redirect
    return HTMLResponse(
        status_code=204,
        headers={"HX-Redirect": "/transactions/"}
    )

@router.get("/transactions/{transaction_id}", response_class=HTMLResponse)
async def view_transaction_page(
    transaction_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Render the transaction detail page"""
    transaction = await transaction_queries.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    categories = await category_queries.list_categories(db)
    
    return templates.TemplateResponse(
        "transactions/detail.html",
        {
            "request": request,
            "transaction": transaction,
            "categories": categories
        }
    )

@router.delete("/transactions/{transaction_id}", response_class=HTMLResponse)
async def delete_transaction_htmx(
    transaction_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a transaction and return success response for HTMX"""
    success = await transaction_queries.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Return empty response with HX-Redirect
    return HTMLResponse(
        status_code=204,
        headers={"HX-Redirect": "/transactions/"}
    )