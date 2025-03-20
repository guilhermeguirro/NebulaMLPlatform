"""
Fraud Detection Service API endpoints.
"""
from fastapi import APIRouter

def init_fraud_detection_api(app):
    """Initialize fraud detection service API endpoints."""
    router = APIRouter(prefix="/fraud", tags=["fraud"])
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint for fraud detection service."""
        return {"status": "healthy"}
    
    app.include_router(router) 