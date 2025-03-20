"""
Transaction Models

This module defines data models for financial transactions,
following clean code principles and best practices.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Optional, Any
from uuid import UUID


class TransactionType(Enum):
    """Types of financial transactions."""
    PAYMENT = auto()
    TRANSFER = auto()
    DEPOSIT = auto()
    WITHDRAWAL = auto()
    REFUND = auto()
    FEE = auto()
    ADJUSTMENT = auto()


class TransactionStatus(Enum):
    """Status of a transaction in its lifecycle."""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    BLOCKED = auto()
    REVERSED = auto()
    CANCELLED = auto()


class RiskLevel(Enum):
    """Risk classification for transactions."""
    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class Transaction:
    """
    Represents a financial transaction.
    
    This model captures all essential information about a transaction
    including its status, parties involved, and risk assessment.
    """
    id: UUID
    amount: float
    currency: str
    timestamp: datetime
    type: TransactionType
    status: TransactionStatus
    sender: Dict[str, Any]
    recipient: Dict[str, Any]
    reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    risk_score: Optional[float] = None
    risk_level: Optional[RiskLevel] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary representation."""
        return {
            "id": str(self.id),
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type.name,
            "status": self.status.name,
            "sender": self.sender,
            "recipient": self.recipient,
            "reference": self.reference,
            "metadata": self.metadata,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.name if self.risk_level else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary representation."""
        return cls(
            id=UUID(data["id"]),
            amount=data["amount"],
            currency=data["currency"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            type=TransactionType[data["type"]],
            status=TransactionStatus[data["status"]],
            sender=data["sender"],
            recipient=data["recipient"],
            reference=data.get("reference"),
            metadata=data.get("metadata", {}),
            risk_score=data.get("risk_score"),
            risk_level=RiskLevel[data["risk_level"]] if data.get("risk_level") else None
        )
    
    def is_cross_border(self) -> bool:
        """Determine if the transaction crosses country borders."""
        return self.sender.get("country_code") != self.recipient.get("country_code")
    
    def is_high_value(self, threshold: float = 10000.0) -> bool:
        """Determine if the transaction is considered high value."""
        return self.amount >= threshold
    
    def is_high_risk(self) -> bool:
        """Determine if the transaction is considered high risk."""
        if self.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            return True
        if self.risk_score is not None and self.risk_score >= 0.7:
            return True
        return False 