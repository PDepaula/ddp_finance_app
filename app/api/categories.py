from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.templates import templates
from app.db import get_db
from app.models.domain import CategoryCreate, Category
from app.queries import categories as category_queries

router = APIRouter()

# --- API Routes (for JSON responses) ---

@router.get("/api/categories/", response_model=List[Category])
async def api_list_categories(
    db: AsyncSession = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """List categories"""
    return await category_queries.list_categories(db, limit, offset)

@router.get("/api/categories/with-counts/")
async def api_list_categories_with_counts(
    db: AsyncSession = Depends(get_db)
):
    """List categories with transaction counts"""
    return await category_queries.list_categories_with_counts(db)

@router.get("/api/categories/{category_id}", response_model=Category)
async def api_get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a category by ID"""
    category = await category_queries.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/api/categories/", response_model=Category)
async def api_create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new category"""
    return await category_queries.create_category(db, category_data)

@router.put("/api/categories/{category_id}", response_model=Category)
async def api_update_category(
    category_id: int,
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a category"""
    category = await category_queries.update_category(
        db, category_id, category_data.dict()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/api/categories/{category_id}")
async def api_delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category"""
    success = await category_queries.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# --- HTML Routes (for HTMX interactions) ---

@router.get("/categories/", response_class=HTMLResponse)
async def list_categories_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Render the categories list page"""
    categories_with_counts = await category_queries.list_categories_with_counts(db)
    
    return templates.TemplateResponse(
        "categories/list.html",
        {
            "request": request,
            "categories": categories_with_counts
        }
    )

@router.get("/categories/new", response_class=HTMLResponse)
async def new_category_page(
    request: Request
):
    """Render the new category form"""
    return templates.TemplateResponse(
        "categories/create.html",
        {"request": request}
    )

@router.post("/categories/", response_class=HTMLResponse)
async def create_category_form(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a category from form data and return partial HTML"""
    # Create category data
    category_data = CategoryCreate(
        name=name,
        description=description
    )
    
    # Save to database
    await category_queries.create_category(db, category_data)
    
    # Redirect to list view using HX-Redirect
    return HTMLResponse(
        status_code=204,
        headers={"HX-Redirect": "/categories/"}
    )

@router.get("/categories/{category_id}", response_class=HTMLResponse)
async def view_category_page(
    category_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Render the category detail page"""
    category = await category_queries.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return templates.TemplateResponse(
        "categories/detail.html",
        {
            "request": request,
            "category": category
        }
    )

@router.delete("/categories/{category_id}", response_class=HTMLResponse)
async def delete_category_htmx(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a category and return success response for HTMX"""
    success = await category_queries.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Return empty response with HX-Redirect
    return HTMLResponse(
        status_code=204,
        headers={"HX-Redirect": "/categories/"}
    )