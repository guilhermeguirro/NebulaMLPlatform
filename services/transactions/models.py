"""
Transaction models for NebulaMLPlatform.
"""
from enum import Enum
from pydantic import BaseModel

class TransactionStatus(str, Enum):
    """Transaction status enum."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    FRAUD = "fraud"

class Transaction(BaseModel):
    """Transaction model."""
    id: str
    amount: float
    status: TransactionStatus
    timestamp: str 