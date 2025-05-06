from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.templates import templates
from app.config import settings
from app.db import get_db, engine
from app.api import transactions, categories
from app.queries import transactions as transaction_queries
from app.queries import categories as category_queries

# Create the FastAPI app
app = FastAPI(title=settings.APP_NAME)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(transactions.router, tags=["transactions"])
app.include_router(categories.router, tags=["categories"])

# Root route
@app.get("/")
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Home page with dashboard"""
    # Get recent transactions
    recent_transactions = await transaction_queries.list_transactions(db, limit=5)
    
    # Get categories with counts
    categories = await category_queries.list_categories_with_counts(db)
    
    # Calculate basic statistics
    total_transactions = sum(cat["transaction_count"] for cat in categories)
    
    # Sum of all transaction amounts
    total_spending = sum(
        transaction.amount if transaction.amount < 0 else 0 
        for transaction in recent_transactions
    )
    total_income = sum(
        transaction.amount if transaction.amount > 0 else 0 
        for transaction in recent_transactions
    )
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "recent_transactions": recent_transactions,
            "categories": categories,
            "stats": {
                "total_transactions": total_transactions,
                "total_spending": abs(total_spending),
                "total_income": total_income,
                "net": total_income + total_spending  # Spending is negative
            }
        }
    )

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)