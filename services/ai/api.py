"""
AI Service API endpoints.
"""
from fastapi import APIRouter

def init_ai_service_api(app):
    """Initialize AI service API endpoints."""
    router = APIRouter(prefix="/ai", tags=["ai"])
    
    @router.get("/health")
    async def health_check():
        """Health check endpoint for AI service."""
        return {"status": "healthy"}
    
    app.include_router(router) 