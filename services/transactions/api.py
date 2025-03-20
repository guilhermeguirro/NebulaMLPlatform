"""
Transactions Service API endpoints.
"""
from fastapi import APIRouter
from .models import Transaction, TransactionStatus

def init_transactions_api(app):
    """Initialize transactions service API endpoints."""
    router = APIRouter(prefix="/transactions", tags=["transactions"])
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint for transactions service."""
        return {"status": "healthy"}
    
    app.include_router(router) 