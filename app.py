#!/usr/bin/env python3
"""
SecureFinStack Main Application

This module serves as the entry point for the SecureFinStack platform,
integrating all components and providing a unified API.
"""

import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from prometheus_client.multiprocess import MultiProcessCollector
from rich.console import Console
from rich.logging import RichHandler

from services.ai.api import init_ai_service_api
from services.fraud.api import init_fraud_detection_api
from services.transactions.api import init_transactions_api
from services.transactions.models import Transaction, TransactionStatus

# Configure logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)
logger = logging.getLogger("securestack")

# Configure OpenTelemetry (if OTLP endpoint is provided)
if "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ:
    resource = Resource.create({"service.name": "securestack-api"})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"])
    )
    trace.get_tracer_provider().add_span_processor(span_processor)
    logger.info(f"OpenTelemetry configured with endpoint: {os.environ['OTEL_EXPORTER_OTLP_ENDPOINT']}")

# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total count of API requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Counter(
    "api_request_latency_seconds",
    "API request latency in seconds",
    ["method", "endpoint"]
)

# Initialize FastAPI app
app = FastAPI(
    title="SecureFinStack API",
    description="Secure Financial Operations Platform API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"]
)

# Add middleware for request ID tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to request and response."""
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = datetime.now()
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Add request ID to response
    response.headers["X-Request-ID"] = request_id
    
    # Record metrics
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc(duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Add middleware for error handling
@app.middleware("http")
async def error_handler(request: Request, call_next):
    """Global error handling middleware."""
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(f"Unhandled exception: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
                "timestamp": datetime.now().isoformat()
            }
        )

# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

# Metrics endpoint
@app.get("/metrics", tags=["system"])
async def metrics():
    """Prometheus metrics endpoint."""
    return JSONResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )

# Custom OpenAPI schema
@app.get("/openapi.json", tags=["documentation"])
async def get_open_api_endpoint():
    """Get OpenAPI schema."""
    return JSONResponse(get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    ))

# Swagger UI
@app.get("/docs", tags=["documentation"])
async def get_documentation():
    """Get Swagger UI."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - API Documentation"
    )

# Initialize component APIs
init_fraud_detection_api(app)
init_ai_service_api(app)
init_transactions_api(app)

# Enable OpenTelemetry instrumentation
if "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ:
    FastAPIInstrumentor.instrument_app(app)

def main():
    """Main entry point for the application."""
    logger.info("Starting SecureFinStack API")
    
    # Get configuration from environment
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", "8000"))
    workers = int(os.environ.get("API_WORKERS", "1"))
    
    # Log configuration
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Workers: {workers}")
    
    # Start server
    if workers == 1:
        # Development mode with auto-reload
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    else:
        # Production mode with multiple workers
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )

if __name__ == "__main__":
    main() 