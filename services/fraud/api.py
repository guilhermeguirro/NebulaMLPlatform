"""
Fraud Detection API

This module provides a RESTful API for fraud detection services,
following clean code principles and best practices.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from .detector import FraudDetectionService, FraudPrediction
from ..transactions.models import Transaction, TransactionStatus, TransactionType

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastAPI router
router = APIRouter(prefix="/api/v1/fraud", tags=["fraud"])

# Initialize fraud detection service (global instance)
fraud_service = FraudDetectionService()


# Request/Response Models
class TransactionParty(BaseModel):
    """Information about a party in a transaction."""
    id: str
    name: str
    country_code: str
    account_id: str
    institution_id: Optional[str] = None


class TransactionRequest(BaseModel):
    """Request model for fraud detection."""
    id: str = Field(..., description="Unique transaction identifier")
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Transaction timestamp")
    type: str = Field(..., description="Transaction type")
    sender: TransactionParty
    recipient: TransactionParty
    reference: Optional[str] = None
    
    @validator("amount")
    def amount_must_be_positive(cls, v: float) -> float:
        """Validate that amount is positive."""
        if v <= 0:
            raise ValueError("Transaction amount must be positive")
        return v
    
    @validator("currency")
    def currency_must_be_valid(cls, v: str) -> str:
        """Validate currency code."""
        valid_currencies = {"USD", "EUR", "GBP", "JPY", "CAD"}
        if v not in valid_currencies:
            raise ValueError(f"Invalid currency: {v}. Must be one of {valid_currencies}")
        return v


class FraudDetectionResponse(BaseModel):
    """Response model for fraud detection."""
    transaction_id: str
    timestamp: datetime
    fraud_probability: float
    is_fraudulent: bool
    confidence: float
    risk_factors: List[str] = Field(default_factory=list)
    recommendation: str
    should_block: bool


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Dependency for request ID tracking
async def get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    if "X-Request-ID" in request.headers:
        return request.headers["X-Request-ID"]
    return str(uuid.uuid4())


@router.post(
    "/detect",
    response_model=FraudDetectionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def detect_fraud(
    transaction: TransactionRequest,
    request_id: str = Depends(get_request_id)
) -> FraudDetectionResponse:
    """
    Detect fraud in a transaction.
    
    Args:
        transaction: Transaction details
        request_id: Request identifier
        
    Returns:
        Fraud detection results
    """
    try:
        logger.info(f"Fraud detection request received for transaction {transaction.id}")
        
        # Convert to domain model
        domain_transaction = _convert_to_domain_model(transaction)
        
        # Process transaction
        prediction = fraud_service.process_transaction(domain_transaction)
        
        # Generate response
        response = FraudDetectionResponse(
            transaction_id=transaction.id,
            timestamp=datetime.now(),
            fraud_probability=prediction.fraud_probability,
            is_fraudulent=prediction.is_fraudulent,
            confidence=prediction.confidence,
            risk_factors=_extract_risk_factors(prediction),
            recommendation=_get_recommendation(prediction),
            should_block=fraud_service.should_block_transaction(prediction)
        )
        
        logger.info(
            f"Fraud detection complete for transaction {transaction.id}. "
            f"Fraud probability: {prediction.fraud_probability:.2f}"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error processing fraud detection request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing fraud detection request"
        )


@router.get(
    "/transaction/{transaction_id}",
    response_model=FraudDetectionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_fraud_prediction(
    transaction_id: str,
    request_id: str = Depends(get_request_id)
) -> FraudDetectionResponse:
    """
    Get fraud prediction for a transaction.
    
    Args:
        transaction_id: Transaction identifier
        request_id: Request identifier
        
    Returns:
        Fraud detection results
    """
    prediction = fraud_service.get_prediction(transaction_id)
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No prediction found for transaction {transaction_id}"
        )
    
    return FraudDetectionResponse(
        transaction_id=transaction_id,
        timestamp=prediction.timestamp,
        fraud_probability=prediction.fraud_probability,
        is_fraudulent=prediction.is_fraudulent,
        confidence=prediction.confidence,
        risk_factors=_extract_risk_factors(prediction),
        recommendation=_get_recommendation(prediction),
        should_block=fraud_service.should_block_transaction(prediction)
    )


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    responses={
        500: {"model": ErrorResponse}
    }
)
async def get_fraud_stats(
    request_id: str = Depends(get_request_id)
) -> Dict[str, Any]:
    """
    Get fraud detection statistics.
    
    Args:
        request_id: Request identifier
        
    Returns:
        Fraud detection statistics
    """
    # In a real implementation, this would provide actual statistics
    return {
        "total_transactions_processed": 0,
        "fraud_detected_count": 0,
        "fraud_rate": 0.0,
        "average_fraud_probability": 0.0,
        "top_risk_factors": [],
        "timestamp": datetime.now()
    }


# Helper functions
def _convert_to_domain_model(tx_request: TransactionRequest) -> Transaction:
    """Convert API request model to domain model."""
    return Transaction(
        id=uuid.UUID(tx_request.id),
        amount=tx_request.amount,
        currency=tx_request.currency,
        timestamp=tx_request.timestamp,
        type=TransactionType[tx_request.type.upper()],
        status=TransactionStatus.PENDING,
        sender=tx_request.sender.dict(),
        recipient=tx_request.recipient.dict(),
        reference=tx_request.reference
    )


def _extract_risk_factors(prediction: FraudPrediction) -> List[str]:
    """Extract risk factors from prediction explanation."""
    if not prediction.explanation:
        return []
        
    # Split explanation into sentences and filter for risk factors
    sentences = prediction.explanation.split(". ")
    risk_factors = [s for s in sentences if "unusual" in s.lower() or "high" in s.lower()]
    
    return risk_factors


def _get_recommendation(prediction: FraudPrediction) -> str:
    """Get recommendation based on fraud prediction."""
    if prediction.fraud_probability > 0.9:
        return "Block transaction and flag for investigation"
    elif prediction.fraud_probability > 0.7:
        return "Request additional verification from user"
    elif prediction.fraud_probability > 0.4:
        return "Apply enhanced monitoring"
    else:
        return "Process transaction normally"


# Integrate with FastAPI
def init_fraud_detection_api(app: FastAPI) -> None:
    """
    Initialize fraud detection API with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.include_router(router)
    
    # Add exception handler for fraud-specific errors
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions."""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                error=str(exc),
                request_id=request.headers.get("X-Request-ID", str(uuid.uuid4())),
                details=None
            ).dict()
        ) 