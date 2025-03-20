"""
Transactions API

This module provides a RESTful API for transaction services,
following clean code principles and best practices.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request, status
from pydantic import BaseModel, Field, validator

from .models import Transaction, TransactionStatus, TransactionType
from ..fraud.detector import FraudDetectionService

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

# Initialize services
fraud_service = FraudDetectionService()

# ----- Models -----

class TransactionParty(BaseModel):
    """Information about a party in a transaction."""
    id: str
    name: str
    country_code: str
    account_id: str
    institution_id: Optional[str] = None


class CreateTransactionRequest(BaseModel):
    """Request model for creating a transaction."""
    amount: float = Field(..., description="Transaction amount")
    currency: str = Field(..., description="Currency code (ISO 4217)")
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


class TransactionResponse(BaseModel):
    """Response model for a transaction."""
    id: str
    amount: float
    currency: str
    timestamp: datetime
    type: str
    status: str
    sender: Dict[str, Any]
    recipient: Dict[str, Any]
    reference: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None


class TransactionUpdateRequest(BaseModel):
    """Request model for updating a transaction."""
    status: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str
    details: Optional[Dict[str, Any]] = None


# ----- Dependencies -----

def get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    return getattr(request.state, "request_id", str(uuid.uuid4()))


# ----- In-memory storage (replace with database in production) -----
transactions_db: Dict[str, Transaction] = {}


# ----- Endpoints -----

@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    request: CreateTransactionRequest,
    request_id: str = Depends(get_request_id)
) -> TransactionResponse:
    """
    Create a new transaction.
    
    This endpoint creates a new transaction and initiates fraud detection.
    """
    logger.info(f"Creating transaction [request_id={request_id}]")
    
    try:
        # Generate transaction ID
        transaction_id = uuid.uuid4()
        
        # Create transaction object
        transaction = Transaction(
            id=transaction_id,
            amount=request.amount,
            currency=request.currency,
            timestamp=datetime.now(),
            type=TransactionType[request.type.upper()],
            status=TransactionStatus.PENDING,
            sender=request.sender.dict(),
            recipient=request.recipient.dict(),
            reference=request.reference
        )
        
        # Store transaction
        transactions_db[str(transaction_id)] = transaction
        
        # Process fraud detection in background (in real app would be async)
        try:
            fraud_prediction = fraud_service.process_transaction(transaction)
            
            # Update transaction with risk information
            transaction.risk_score = fraud_prediction.fraud_probability
            
            # Update status based on fraud detection
            if fraud_service.should_block_transaction(fraud_prediction):
                transaction.status = TransactionStatus.BLOCKED
                logger.warning(f"Transaction {transaction_id} blocked due to fraud risk")
            
        except Exception as e:
            logger.error(f"Error during fraud detection: {str(e)}")
            # Continue processing the transaction despite fraud detection issues
        
        logger.info(f"Transaction {transaction_id} created with status {transaction.status}")
        
        # Return response
        return TransactionResponse(
            id=str(transaction_id),
            amount=transaction.amount,
            currency=transaction.currency,
            timestamp=transaction.timestamp,
            type=transaction.type.name,
            status=transaction.status.name,
            sender=transaction.sender,
            recipient=transaction.recipient,
            reference=transaction.reference,
            risk_score=transaction.risk_score,
            risk_level=transaction.risk_level.name if transaction.risk_level else None
        )
        
    except Exception as e:
        logger.exception(f"Error creating transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to create transaction", "details": str(e)}
        )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse
)
async def get_transaction(
    transaction_id: str,
    request_id: str = Depends(get_request_id)
) -> TransactionResponse:
    """
    Get a transaction by ID.
    """
    logger.info(f"Retrieving transaction {transaction_id} [request_id={request_id}]")
    
    if transaction_id not in transactions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    transaction = transactions_db[transaction_id]
    
    return TransactionResponse(
        id=str(transaction.id),
        amount=transaction.amount,
        currency=transaction.currency,
        timestamp=transaction.timestamp,
        type=transaction.type.name,
        status=transaction.status.name,
        sender=transaction.sender,
        recipient=transaction.recipient,
        reference=transaction.reference,
        risk_score=transaction.risk_score,
        risk_level=transaction.risk_level.name if transaction.risk_level else None
    )


@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse
)
async def update_transaction(
    transaction_id: str,
    request: TransactionUpdateRequest,
    request_id: str = Depends(get_request_id)
) -> TransactionResponse:
    """
    Update a transaction.
    """
    logger.info(f"Updating transaction {transaction_id} [request_id={request_id}]")
    
    if transaction_id not in transactions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {transaction_id} not found"
        )
    
    transaction = transactions_db[transaction_id]
    
    # Update fields
    if request.status:
        try:
            transaction.status = TransactionStatus[request.status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {request.status}"
            )
    
    if request.risk_score is not None:
        transaction.risk_score = request.risk_score
    
    if request.risk_level:
        try:
            from .models import RiskLevel
            transaction.risk_level = RiskLevel[request.risk_level.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid risk level: {request.risk_level}"
            )
    
    logger.info(f"Transaction {transaction_id} updated")
    
    return TransactionResponse(
        id=str(transaction.id),
        amount=transaction.amount,
        currency=transaction.currency,
        timestamp=transaction.timestamp,
        type=transaction.type.name,
        status=transaction.status.name,
        sender=transaction.sender,
        recipient=transaction.recipient,
        reference=transaction.reference,
        risk_score=transaction.risk_score,
        risk_level=transaction.risk_level.name if transaction.risk_level else None
    )


@router.get(
    "/",
    response_model=List[TransactionResponse]
)
async def list_transactions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    request_id: str = Depends(get_request_id)
) -> List[TransactionResponse]:
    """
    List transactions with optional filtering.
    """
    logger.info(f"Listing transactions [request_id={request_id}]")
    
    # Filter transactions
    filtered_transactions = list(transactions_db.values())
    
    if status:
        try:
            status_enum = TransactionStatus[status.upper()]
            filtered_transactions = [
                tx for tx in filtered_transactions 
                if tx.status == status_enum
            ]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
    
    # Apply pagination
    paginated = filtered_transactions[offset:offset+limit]
    
    # Convert to response models
    return [
        TransactionResponse(
            id=str(tx.id),
            amount=tx.amount,
            currency=tx.currency,
            timestamp=tx.timestamp,
            type=tx.type.name,
            status=tx.status.name,
            sender=tx.sender,
            recipient=tx.recipient,
            reference=tx.reference,
            risk_score=tx.risk_score,
            risk_level=tx.risk_level.name if tx.risk_level else None
        )
        for tx in paginated
    ]


# ----- API Initialization -----

def init_transactions_api(app: FastAPI) -> None:
    """Initialize transactions API with FastAPI app."""
    app.include_router(router)
    logger.info("Transactions API initialized") 