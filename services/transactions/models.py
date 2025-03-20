"""
Transaction data models for SecureFinStack platform.

This module provides immutable data models for representing financial transactions
with proper type annotations and validation.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Tuple, TypedDict, Union
from uuid import UUID

# Immutable constants
MAX_TRANSACTION_AMOUNT = 1_000_000.00
RESTRICTED_COUNTRIES: FrozenSet[str] = frozenset(["NK", "IR", "CU", "SY"])
ELEVATED_RISK_THRESHOLD = 50_000.00
AUTHORIZED_CURRENCIES: FrozenSet[str] = frozenset(["USD", "EUR", "GBP", "JPY", "CAD"])


class TransactionStatus(Enum):
    """Status of a financial transaction."""
    PENDING = auto()
    APPROVED = auto()
    REJECTED = auto()
    FLAGGED_FOR_REVIEW = auto()
    COMPLETED = auto()
    REFUNDED = auto()
    FAILED = auto()


class TransactionType(Enum):
    """Type of financial transaction."""
    PAYMENT = auto()
    TRANSFER = auto()
    WITHDRAWAL = auto()
    DEPOSIT = auto()
    FEE = auto()
    REFUND = auto()
    ADJUSTMENT = auto()


class RiskLevel(Enum):
    """Risk level assigned to a transaction."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class TransactionPartyInfo(TypedDict):
    """Information about a party involved in a transaction."""
    id: str
    name: str
    country_code: str
    account_id: str
    institution_id: Optional[str]


@dataclass(frozen=True)
class Transaction:
    """
    Immutable representation of a financial transaction.
    
    Attributes:
        id: Unique identifier for the transaction
        amount: Transaction amount
        currency: Currency code (ISO 4217)
        timestamp: When the transaction was initiated
        type: Type of transaction
        status: Current status of the transaction
        sender: Information about the sending party
        recipient: Information about the receiving party
        reference: Optional reference code
        risk_score: Calculated risk score (0.0-1.0)
    """
    id: UUID
    amount: float
    currency: str
    timestamp: datetime
    type: TransactionType
    status: TransactionStatus
    sender: TransactionPartyInfo
    recipient: TransactionPartyInfo
    reference: Optional[str] = None
    risk_score: Optional[float] = None
    
    def __post_init__(self) -> None:
        """Validate transaction data on initialization."""
        object.__setattr__(self, "risk_score", self._calculate_risk_score())
        
        # Validate currency
        if self.currency not in AUTHORIZED_CURRENCIES:
            raise ValueError(f"Currency {self.currency} is not supported")
        
        # Validate amount
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        if self.amount > MAX_TRANSACTION_AMOUNT:
            raise ValueError(f"Amount exceeds maximum allowed: {MAX_TRANSACTION_AMOUNT}")
    
    def _calculate_risk_score(self) -> float:
        """
        Calculate risk score based on transaction attributes.
        
        Returns:
            float: Risk score between 0.0 and 1.0
        """
        score = 0.0
        
        # Check amount
        if self.amount > ELEVATED_RISK_THRESHOLD:
            score += 0.3
        
        # Check countries
        sender_country = self.sender["country_code"]
        recipient_country = self.recipient["country_code"]
        
        if sender_country in RESTRICTED_COUNTRIES or recipient_country in RESTRICTED_COUNTRIES:
            score += 0.5
        
        # Cross-border check
        if sender_country != recipient_country:
            score += 0.2
        
        return min(score, 1.0)
    
    def with_updated_status(self, new_status: TransactionStatus) -> "Transaction":
        """
        Return a new Transaction with updated status.
        
        Args:
            new_status: The new transaction status
            
        Returns:
            A new Transaction instance with the updated status
        """
        return Transaction(
            id=self.id,
            amount=self.amount,
            currency=self.currency,
            timestamp=self.timestamp,
            type=self.type,
            status=new_status,
            sender=self.sender,
            recipient=self.recipient,
            reference=self.reference
        )
    
    def get_risk_level(self) -> RiskLevel:
        """
        Determine risk level based on risk score.
        
        Returns:
            RiskLevel: The calculated risk level
        """
        if self.risk_score is None:
            return RiskLevel.LOW
            
        if self.risk_score < 0.3:
            return RiskLevel.LOW
        elif self.risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif self.risk_score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def to_dict(self) -> Dict:
        """
        Convert transaction to dictionary representation.
        
        Returns:
            Dictionary representation of the transaction
        """
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
            "risk_score": self.risk_score,
            "risk_level": self.get_risk_level().name
        }


def categorize_transactions(
    transactions: List[Transaction]
) -> Dict[RiskLevel, List[Transaction]]:
    """
    Categorize transactions by risk level.
    
    Args:
        transactions: List of transactions to categorize
        
    Returns:
        Dictionary mapping risk levels to lists of transactions
    """
    result: Dict[RiskLevel, List[Transaction]] = {
        RiskLevel.LOW: [],
        RiskLevel.MEDIUM: [],
        RiskLevel.HIGH: [],
        RiskLevel.CRITICAL: []
    }
    
    for transaction in transactions:
        risk_level = transaction.get_risk_level()
        result[risk_level].append(transaction)
    
    return result 