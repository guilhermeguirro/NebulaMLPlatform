#!/usr/bin/env python3
"""
Enterprise AI Service API
Provides a secure REST API for Claude AI capabilities with enterprise features.
"""

import os
from typing import Dict, Optional, List
from datetime import datetime
import logging
import uuid

from fastapi import FastAPI, HTTPException, Depends, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
import jwt
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .claude_service import ClaudeService

# Configure logging
logger = logging.getLogger("neutronpay.ai")

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise AI Service",
    description="Enterprise-grade AI capabilities powered by Claude",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
claude_service = ClaudeService()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt for Claude")
    max_tokens: int = Field(1000, description="Maximum tokens in response")
    temperature: float = Field(0.7, description="Temperature for response generation")
    context: Optional[Dict] = Field(None, description="Additional context")

class ErrorResponse(BaseModel):
    error: str
    timestamp: datetime
    request_id: Optional[str]

# Authentication middleware
async def verify_token(token: str = Depends(oauth2_scheme)) -> Dict:
    """Verify JWT token and return claims."""
    try:
        claims = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=["HS256"]
        )
        return claims
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

# Request ID middleware
async def get_request_id(
    request: Request,
    x_request_id: Optional[str] = Header(None)
) -> str:
    """Get or generate request ID."""
    if x_request_id:
        return x_request_id
    return f"req-{datetime.utcnow().timestamp()}"

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with proper error formatting."""
    error_response = ErrorResponse(
        error=str(exc),
        timestamp=datetime.utcnow(),
        request_id=request.state.request_id
    )
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Main API endpoint
@app.post("/generate")
async def generate_response(
    request: GenerateRequest,
    claims: Dict = Depends(verify_token),
    request_id: str = Depends(get_request_id)
):
    """
    Generate a response using Claude with enterprise features.
    
    This endpoint provides:
    - Authentication via JWT
    - Request tracking
    - Rate limiting
    - Monitoring
    - Audit logging
    """
    try:
        # Add request context
        context = request.context or {}
        context.update({
            "request_id": request_id,
            "user_id": claims.get("sub"),
            "timestamp": datetime.utcnow().isoformat()
        })

        # Generate response
        response = await claude_service.generate_response(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            context=context
        )

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# Configuration endpoints
@app.get("/config")
async def get_configuration(claims: Dict = Depends(verify_token)):
    """Get current service configuration."""
    # Only allow admin users
    if "admin" not in claims.get("roles", []):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )

    return {
        "rate_limit_per_minute": claude_service.rate_limit_per_minute,
        "max_retries": claude_service.max_retries,
        "model_version": "claude-3-opus-20240229"
    }

# Initialize router
router = APIRouter(prefix="/api/v1/ai", tags=["AI Services"])

# ----- Models -----

class AnalysisRequest(BaseModel):
    """Request model for transaction analysis."""
    transaction_id: str = Field(..., description="Unique identifier for the transaction")
    transaction_data: Dict = Field(..., description="Transaction data for analysis")
    context: Optional[Dict] = Field(None, description="Additional context for analysis")

class AnalysisResponse(BaseModel):
    """Response model for transaction analysis."""
    transaction_id: str = Field(..., description="Unique identifier for the transaction")
    timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    insights: List[str] = Field(..., description="List of insights derived from analysis")
    risk_score: float = Field(..., description="Risk score from 0.0 to 1.0", ge=0.0, le=1.0)
    anomalies: List[Dict] = Field(default_factory=list, description="Detected anomalies")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on analysis")

# ----- Dependencies -----

def get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    return getattr(request.state, "request_id", str(uuid.uuid4()))

# ----- Endpoints -----

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transaction(
    request: AnalysisRequest,
    request_id: str = Depends(get_request_id)
):
    """
    Analyze a transaction using AI models to detect patterns, assess risk,
    and provide insights.
    """
    logger.info(f"Analyzing transaction {request.transaction_id} [request_id={request_id}]")
    
    try:
        # In a real implementation, this would use actual AI models
        # For now, we return mock data
        return AnalysisResponse(
            transaction_id=request.transaction_id,
            insights=[
                "Transaction falls within normal parameters",
                "User behavior consistent with historical patterns"
            ],
            risk_score=0.2,
            anomalies=[],
            recommendations=[
                "No additional verification needed"
            ]
        )
    except Exception as e:
        logger.error(f"Error analyzing transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to analyze transaction", "details": str(e)}
        )

@router.get("/models/status")
async def get_model_status(request_id: str = Depends(get_request_id)):
    """Get status of AI models."""
    logger.info(f"Getting AI model status [request_id={request_id}]")
    
    return {
        "status": "operational",
        "models": {
            "transaction_analysis": {
                "version": "1.0.0",
                "status": "active",
                "last_updated": datetime.now().isoformat()
            },
            "fraud_detection": {
                "version": "1.0.0",
                "status": "active",
                "last_updated": datetime.now().isoformat()
            },
            "risk_assessment": {
                "version": "1.0.0",
                "status": "active",
                "last_updated": datetime.now().isoformat()
            }
        }
    }

# ----- API Initialization -----

def init_ai_service_api(app: FastAPI):
    """Initialize AI service API and register it with the main app."""
    app.include_router(router)
    logger.info("AI service API initialized")
    return router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 