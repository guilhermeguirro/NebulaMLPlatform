#!/usr/bin/env python3
"""
Enterprise AI Service API
Provides a secure REST API for Claude AI capabilities with enterprise features.
"""

import os
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
import jwt
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .claude_service import ClaudeService

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 