"""
Unit tests for fraud detection API.

These tests verify the functionality of the fraud detection API endpoints,
focusing on request handling, validation, and integration with the fraud detection service.
"""

import json
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ..api import (
    router,
    init_fraud_detection_api,
    FraudDetectionResponse,
    TransactionRequest,
    ErrorResponse,
    detect_fraud,
    get_fraud_prediction
)
from ..detector import FraudDetectionService, FraudPrediction


@pytest.fixture
def app():
    """Fixture providing a FastAPI application."""
    app = FastAPI()
    init_fraud_detection_api(app)
    return app


@pytest.fixture
def client(app):
    """Fixture providing a test client."""
    return TestClient(app)


@pytest.fixture
def valid_transaction_data():
    """Fixture providing valid transaction data."""
    return {
        "id": str(uuid.uuid4()),
        "amount": 1000.00,
        "currency": "USD",
        "timestamp": datetime.now().isoformat(),
        "type": "PAYMENT",
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
        "reference": "INV-001"
    }


@pytest.fixture
def high_risk_transaction_data():
    """Fixture providing high-risk transaction data."""
    return {
        "id": str(uuid.uuid4()),
        "amount": 50000.00,
        "currency": "USD",
        "timestamp": datetime(2023, 5, 15, 2, 30).isoformat(),
        "type": "PAYMENT",
        "sender": {
            "id": "user123",
            "name": "John Doe",
            "country_code": "US",
            "account_id": "acc123",
            "institution_id": "bank123"
        },
        "recipient": {
            "id": "user789",
            "name": "Foreign Recipient",
            "country_code": "IR",
            "account_id": "acc789",
            "institution_id": "bank789"
        },
        "reference": "INV-002"
    }


@pytest.fixture
def mock_fraud_prediction():
    """Fixture providing a mock fraud prediction."""
    return FraudPrediction(
        transaction_id="tx123",
        fraud_probability=0.2,
        is_fraudulent=False,
        confidence=0.9,
        timestamp=datetime.now(),
        feature_importance={"amount": 0.15, "unusual_location": 0.1},
        explanation="Transaction appears legitimate. Normal transaction frequency."
    )


@pytest.fixture
def mock_high_risk_prediction():
    """Fixture providing a mock high-risk fraud prediction."""
    return FraudPrediction(
        transaction_id="tx456",
        fraud_probability=0.8,
        is_fraudulent=True,
        confidence=0.9,
        timestamp=datetime.now(),
        feature_importance={"amount": 0.15, "unusual_location": 0.5},
        explanation="Transaction shows high fraud risk patterns. Transaction location is unusual for this user."
    )


class TestTransactionRequest:
    """Tests for TransactionRequest validation."""

    def test_valid_transaction(self, valid_transaction_data):
        """Test creating a valid transaction request."""
        request = TransactionRequest(**valid_transaction_data)
        assert request.id == valid_transaction_data["id"]
        assert request.amount == valid_transaction_data["amount"]
        assert request.type == valid_transaction_data["type"]

    def test_negative_amount(self, valid_transaction_data):
        """Test that negative amounts are rejected."""
        valid_transaction_data["amount"] = -100.0
        with pytest.raises(ValidationError):
            TransactionRequest(**valid_transaction_data)

    def test_invalid_currency(self, valid_transaction_data):
        """Test that invalid currencies are rejected."""
        valid_transaction_data["currency"] = "XYZ"
        with pytest.raises(ValidationError):
            TransactionRequest(**valid_transaction_data)


class TestDetectFraudEndpoint:
    """Tests for the detect_fraud endpoint."""

    @patch.object(FraudDetectionService, 'process_transaction')
    def test_detect_fraud_success(self, mock_process, client, valid_transaction_data, mock_fraud_prediction):
        """Test successful fraud detection."""
        # Setup mock
        mock_process.return_value = mock_fraud_prediction
        
        # Make request
        response = client.post(
            "/api/v1/fraud/detect",
            json=valid_transaction_data,
            headers={"X-Request-ID": "test-123"}
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["transaction_id"] == valid_transaction_data["id"]
        assert not result["is_fraudulent"]
        assert "recommendation" in result

    @patch.object(FraudDetectionService, 'process_transaction')
    def test_detect_fraud_high_risk(self, mock_process, client, high_risk_transaction_data, mock_high_risk_prediction):
        """Test high-risk fraud detection."""
        # Setup mock
        mock_process.return_value = mock_high_risk_prediction
        
        # Make request
        response = client.post(
            "/api/v1/fraud/detect",
            json=high_risk_transaction_data,
            headers={"X-Request-ID": "test-456"}
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["transaction_id"] == high_risk_transaction_data["id"]
        assert result["is_fraudulent"]
        assert "risk_factors" in result
        assert len(result["risk_factors"]) > 0

    def test_detect_fraud_invalid_data(self, client):
        """Test handling invalid transaction data."""
        # Invalid data (missing required fields)
        invalid_data = {
            "id": str(uuid.uuid4()),
            "amount": 1000.00
            # Missing other required fields
        }
        
        response = client.post(
            "/api/v1/fraud/detect",
            json=invalid_data,
            headers={"X-Request-ID": "test-invalid"}
        )
        
        # Check response
        assert response.status_code == 422  # Validation error

    @patch.object(FraudDetectionService, 'process_transaction')
    def test_detect_fraud_service_error(self, mock_process, client, valid_transaction_data):
        """Test handling service errors."""
        # Setup mock to raise an exception
        mock_process.side_effect = Exception("Service error")
        
        # Make request
        response = client.post(
            "/api/v1/fraud/detect",
            json=valid_transaction_data,
            headers={"X-Request-ID": "test-error"}
        )
        
        # Check response
        assert response.status_code == 500
        result = response.json()
        assert "error" in result


class TestGetFraudPredictionEndpoint:
    """Tests for the get_fraud_prediction endpoint."""

    @patch.object(FraudDetectionService, 'get_prediction')
    def test_get_prediction_success(self, mock_get_prediction, client, mock_fraud_prediction):
        """Test retrieving a prediction successfully."""
        # Setup mock
        transaction_id = "tx123"
        mock_get_prediction.return_value = mock_fraud_prediction
        
        # Make request
        response = client.get(
            f"/api/v1/fraud/transaction/{transaction_id}",
            headers={"X-Request-ID": "test-get"}
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert result["transaction_id"] == transaction_id
        assert not result["is_fraudulent"]

    @patch.object(FraudDetectionService, 'get_prediction')
    def test_get_prediction_not_found(self, mock_get_prediction, client):
        """Test handling non-existent predictions."""
        # Setup mock to return None (prediction not found)
        mock_get_prediction.return_value = None
        
        # Make request
        response = client.get(
            "/api/v1/fraud/transaction/non-existent",
            headers={"X-Request-ID": "test-not-found"}
        )
        
        # Check response
        assert response.status_code == 404
        result = response.json()
        assert "error" in result
        assert "not found" in result["error"].lower()


class TestFraudStatsEndpoint:
    """Tests for the fraud_stats endpoint."""

    def test_get_fraud_stats(self, client):
        """Test retrieving fraud statistics."""
        # Make request
        response = client.get(
            "/api/v1/fraud/stats",
            headers={"X-Request-ID": "test-stats"}
        )
        
        # Check response
        assert response.status_code == 200
        result = response.json()
        assert "total_transactions_processed" in result
        assert "fraud_rate" in result
        assert "timestamp" in result


class TestHelperFunctions:
    """Tests for API helper functions."""

    def test_extract_risk_factors(self):
        """Test extracting risk factors from explanation."""
        from ..api import _extract_risk_factors
        
        # Create mock prediction with explanation
        prediction = MagicMock()
        prediction.explanation = (
            "Transaction shows high fraud risk patterns. "
            "Transaction location is unusual for this user. "
            "Unusually high transaction frequency in the last hour."
        )
        
        risk_factors = _extract_risk_factors(prediction)
        
        # Should extract sentences with "unusual" or "high"
        assert len(risk_factors) == 2
        assert any("location" in factor for factor in risk_factors)
        assert any("frequency" in factor for factor in risk_factors)

    def test_get_recommendation(self):
        """Test getting recommendations based on fraud probability."""
        from ..api import _get_recommendation
        
        # Test different risk levels
        low_risk = MagicMock()
        low_risk.fraud_probability = 0.2
        assert "normal" in _get_recommendation(low_risk).lower()
        
        medium_risk = MagicMock()
        medium_risk.fraud_probability = 0.5
        assert "monitor" in _get_recommendation(medium_risk).lower()
        
        high_risk = MagicMock()
        high_risk.fraud_probability = 0.75
        assert "verification" in _get_recommendation(high_risk).lower()
        
        very_high_risk = MagicMock()
        very_high_risk.fraud_probability = 0.95
        assert "block" in _get_recommendation(very_high_risk).lower() 