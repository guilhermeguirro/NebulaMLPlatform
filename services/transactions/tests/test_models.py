"""
Unit tests for transaction models.

These tests verify the functionality of the transaction models,
focusing on immutability, validation, and risk assessment.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from ..models import (
    Transaction,
    TransactionStatus,
    TransactionType,
    RiskLevel,
    categorize_transactions,
    MAX_TRANSACTION_AMOUNT,
    RESTRICTED_COUNTRIES,
)


@pytest.fixture
def valid_transaction_data():
    """Fixture providing valid transaction data."""
    return {
        "id": uuid4(),
        "amount": 1000.00,
        "currency": "USD",
        "timestamp": datetime.now(),
        "type": TransactionType.PAYMENT,
        "status": TransactionStatus.PENDING,
        "sender": {
            "id": "user123",
            "name": "John Doe",
            "country_code": "US",
            "account_id": "acc123",
            "institution_id": "bank123"
        },
        "recipient": {
            "id": "user456",
            "name": "Jane Smith",
            "country_code": "US",
            "account_id": "acc456",
            "institution_id": "bank456"
        },
        "reference": "INV-001",
    }


class TestTransaction:
    """Test suite for the Transaction class."""

    def test_create_valid_transaction(self, valid_transaction_data):
        """Test creating a valid transaction."""
        transaction = Transaction(**valid_transaction_data)
        assert transaction.id == valid_transaction_data["id"]
        assert transaction.amount == valid_transaction_data["amount"]
        assert transaction.status == TransactionStatus.PENDING
        assert transaction.risk_score is not None
        assert 0.0 <= transaction.risk_score <= 1.0

    def test_immutability(self, valid_transaction_data):
        """Test that Transaction objects are immutable."""
        transaction = Transaction(**valid_transaction_data)
        with pytest.raises(AttributeError):
            transaction.amount = 2000.00

    def test_with_updated_status(self, valid_transaction_data):
        """Test creating a new transaction with updated status."""
        transaction = Transaction(**valid_transaction_data)
        new_transaction = transaction.with_updated_status(TransactionStatus.APPROVED)
        
        # Original transaction should be unchanged
        assert transaction.status == TransactionStatus.PENDING
        
        # New transaction should have updated status
        assert new_transaction.status == TransactionStatus.APPROVED
        
        # All other attributes should be the same
        assert new_transaction.id == transaction.id
        assert new_transaction.amount == transaction.amount

    def test_invalid_currency(self, valid_transaction_data):
        """Test that invalid currencies are rejected."""
        valid_transaction_data["currency"] = "XYZ"
        with pytest.raises(ValueError):
            Transaction(**valid_transaction_data)

    def test_negative_amount(self, valid_transaction_data):
        """Test that negative amounts are rejected."""
        valid_transaction_data["amount"] = -100.00
        with pytest.raises(ValueError):
            Transaction(**valid_transaction_data)

    def test_exceeding_maximum_amount(self, valid_transaction_data):
        """Test that amounts exceeding the maximum are rejected."""
        valid_transaction_data["amount"] = MAX_TRANSACTION_AMOUNT + 1
        with pytest.raises(ValueError):
            Transaction(**valid_transaction_data)

    def test_risk_score_calculation_normal(self, valid_transaction_data):
        """Test risk score calculation for a normal transaction."""
        transaction = Transaction(**valid_transaction_data)
        assert transaction.risk_score == 0.0  # Same country, low amount

    def test_risk_score_calculation_high_amount(self, valid_transaction_data):
        """Test risk score calculation for a high-amount transaction."""
        valid_transaction_data["amount"] = 100000.00
        transaction = Transaction(**valid_transaction_data)
        assert transaction.risk_score == 0.3  # High amount but same country

    def test_risk_score_calculation_restricted_country(self, valid_transaction_data):
        """Test risk score calculation for a restricted country."""
        valid_transaction_data["recipient"]["country_code"] = next(iter(RESTRICTED_COUNTRIES))
        transaction = Transaction(**valid_transaction_data)
        # Restricted country (0.5) + cross-border (0.2)
        assert transaction.risk_score == 0.7

    def test_risk_score_calculation_cross_border(self, valid_transaction_data):
        """Test risk score calculation for a cross-border transaction."""
        valid_transaction_data["recipient"]["country_code"] = "CA"
        transaction = Transaction(**valid_transaction_data)
        assert transaction.risk_score == 0.2  # Cross-border only

    def test_risk_score_calculation_maximum(self, valid_transaction_data):
        """Test risk score calculation maxes out at 1.0."""
        valid_transaction_data["amount"] = 100000.00
        valid_transaction_data["recipient"]["country_code"] = next(iter(RESTRICTED_COUNTRIES))
        transaction = Transaction(**valid_transaction_data)
        # High amount (0.3) + restricted country (0.5) + cross-border (0.2) = 1.0
        assert transaction.risk_score == 1.0

    def test_get_risk_level(self, valid_transaction_data):
        """Test risk level determination based on risk score."""
        # Low risk
        transaction = Transaction(**valid_transaction_data)
        assert transaction.get_risk_level() == RiskLevel.LOW
        
        # Medium risk
        valid_transaction_data["amount"] = 100000.00
        medium_risk = Transaction(**valid_transaction_data)
        assert medium_risk.get_risk_level() == RiskLevel.MEDIUM
        
        # High risk
        valid_transaction_data["recipient"]["country_code"] = "CA"
        high_risk = Transaction(**valid_transaction_data)
        assert high_risk.get_risk_level() == RiskLevel.HIGH
        
        # Critical risk
        valid_transaction_data["recipient"]["country_code"] = next(iter(RESTRICTED_COUNTRIES))
        critical_risk = Transaction(**valid_transaction_data)
        assert critical_risk.get_risk_level() == RiskLevel.CRITICAL

    def test_to_dict(self, valid_transaction_data):
        """Test conversion to dictionary representation."""
        transaction = Transaction(**valid_transaction_data)
        dict_repr = transaction.to_dict()
        
        assert isinstance(dict_repr, dict)
        assert dict_repr["id"] == str(valid_transaction_data["id"])
        assert dict_repr["amount"] == valid_transaction_data["amount"]
        assert dict_repr["type"] == TransactionType.PAYMENT.name
        assert dict_repr["risk_level"] == RiskLevel.LOW.name


class TestTransactionCategories:
    """Test suite for transaction categorization functions."""

    def test_categorize_transactions(self, valid_transaction_data):
        """Test categorization of transactions by risk level."""
        # Create transactions with different risk levels
        low_risk = Transaction(**valid_transaction_data)
        
        valid_transaction_data["amount"] = 100000.00
        medium_risk = Transaction(**valid_transaction_data)
        
        valid_transaction_data["recipient"]["country_code"] = "CA"
        high_risk = Transaction(**valid_transaction_data)
        
        valid_transaction_data["recipient"]["country_code"] = next(iter(RESTRICTED_COUNTRIES))
        critical_risk = Transaction(**valid_transaction_data)
        
        # Categorize the transactions
        transactions = [low_risk, medium_risk, high_risk, critical_risk]
        categorized = categorize_transactions(transactions)
        
        # Verify categorization
        assert len(categorized[RiskLevel.LOW]) == 1
        assert len(categorized[RiskLevel.MEDIUM]) == 0  # Changed to high due to amount and country
        assert len(categorized[RiskLevel.HIGH]) == 1
        assert len(categorized[RiskLevel.CRITICAL]) == 2  # Both high and critical ones

    def test_categorize_empty_list(self):
        """Test categorization with an empty list."""
        result = categorize_transactions([])
        assert len(result[RiskLevel.LOW]) == 0
        assert len(result[RiskLevel.MEDIUM]) == 0
        assert len(result[RiskLevel.HIGH]) == 0
        assert len(result[RiskLevel.CRITICAL]) == 0 