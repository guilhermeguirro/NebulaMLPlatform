"""
Unit tests for fraud detection service.

These tests verify the functionality of the fraud detection service,
following the practices of thorough unit testing.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import uuid4

import numpy as np

from ..detector import (
    FraudDetectionModel,
    FraudDetectionService,
    FeatureExtractor,
    TransactionFeatures,
    FraudPrediction,
    FEATURE_NAMES,
)
from ...transactions.models import Transaction, TransactionStatus, TransactionType


@pytest.fixture
def valid_transaction():
    """Fixture providing a valid transaction for testing."""
    return Transaction(
        id=uuid4(),
        amount=1000.00,
        currency="USD",
        timestamp=datetime.now(),
        type=TransactionType.PAYMENT,
        status=TransactionStatus.PENDING,
        sender={
            "id": "user123",
            "name": "John Doe",
            "country_code": "US",
            "account_id": "acc123",
            "institution_id": "bank123"
        },
        recipient={
            "id": "user456",
            "name": "Jane Smith",
            "country_code": "US",
            "account_id": "acc456",
            "institution_id": "bank456"
        },
        reference="INV-001"
    )


@pytest.fixture
def high_risk_transaction():
    """Fixture providing a high-risk transaction for testing."""
    return Transaction(
        id=uuid4(),
        amount=50000.00,
        currency="USD",
        timestamp=datetime(2023, 5, 15, 2, 30),  # Unusual hour (2:30 AM)
        type=TransactionType.PAYMENT,
        status=TransactionStatus.PENDING,
        sender={
            "id": "user123",
            "name": "John Doe",
            "country_code": "US",
            "account_id": "acc123",
            "institution_id": "bank123"
        },
        recipient={
            "id": "user789",
            "name": "Foreign Recipient",
            "country_code": "IR",  # Restricted country
            "account_id": "acc789",
            "institution_id": "bank789"
        },
        reference="INV-002"
    )


@pytest.fixture
def transaction_history():
    """Fixture providing transaction history for testing."""
    return [
        Transaction(
            id=uuid4(),
            amount=500.00,
            currency="USD",
            timestamp=datetime.now() - timedelta(days=5),
            type=TransactionType.PAYMENT,
            status=TransactionStatus.COMPLETED,
            sender={
                "id": "user123",
                "name": "John Doe",
                "country_code": "US",
                "account_id": "acc123",
                "institution_id": "bank123"
            },
            recipient={
                "id": "user456",
                "name": "Jane Smith",
                "country_code": "US",
                "account_id": "acc456",
                "institution_id": "bank456"
            },
            reference="HIST-001"
        ),
        Transaction(
            id=uuid4(),
            amount=750.00,
            currency="USD",
            timestamp=datetime.now() - timedelta(days=2),
            type=TransactionType.PAYMENT,
            status=TransactionStatus.COMPLETED,
            sender={
                "id": "user123",
                "name": "John Doe",
                "country_code": "US",
                "account_id": "acc123",
                "institution_id": "bank123"
            },
            recipient={
                "id": "user456",
                "name": "Jane Smith",
                "country_code": "US",
                "account_id": "acc456",
                "institution_id": "bank456"
            },
            reference="HIST-002"
        )
    ]


@pytest.fixture
def feature_extractor(transaction_history):
    """Fixture providing a feature extractor with history."""
    extractor = FeatureExtractor(transaction_history)
    return extractor


@pytest.fixture
def sample_features():
    """Fixture providing sample transaction features."""
    return TransactionFeatures(
        features={
            "amount": 1000.0,
            "is_cross_border": 0.0,
            "transaction_velocity_1h": 0.0,
            "transaction_velocity_24h": 1.0,
            "transaction_velocity_7d": 2.0,
            "unusual_hour": 0.0,
            "unusual_location": 0.0,
            "unusual_merchant_category": 0.0,
            "recipient_risk_score": 0.0,
            "transaction_risk_score": 0.2,
            "amount_percentile": 0.5,
        },
        transaction_id=uuid4(),
        timestamp=datetime.now()
    )


@pytest.fixture
def high_risk_features():
    """Fixture providing high-risk transaction features."""
    return TransactionFeatures(
        features={
            "amount": 50000.0,
            "is_cross_border": 1.0,
            "transaction_velocity_1h": 5.0,
            "transaction_velocity_24h": 10.0,
            "transaction_velocity_7d": 15.0,
            "unusual_hour": 1.0,
            "unusual_location": 1.0,
            "unusual_merchant_category": 0.0,
            "recipient_risk_score": 0.8,
            "transaction_risk_score": 0.9,
            "amount_percentile": 0.95,
        },
        transaction_id=uuid4(),
        timestamp=datetime.now()
    )


class TestTransactionFeatures:
    """Test suite for the TransactionFeatures class."""

    def test_to_array(self, sample_features):
        """Test conversion to numpy array."""
        array = sample_features.to_array()
        assert isinstance(array, np.ndarray)
        assert len(array) == len(FEATURE_NAMES)
        
        # Check array values
        for i, feature_name in enumerate(FEATURE_NAMES):
            expected_value = sample_features.features.get(feature_name, 0.0)
            assert array[i] == expected_value

    def test_get_feature_value(self, sample_features):
        """Test getting a specific feature value."""
        amount = sample_features.get_feature_value("amount")
        assert amount == 1000.0
        
        # Non-existent feature
        non_existent = sample_features.get_feature_value("non_existent")
        assert non_existent == 0.0

    def test_with_additional_feature(self, sample_features):
        """Test adding a new feature."""
        updated = sample_features.with_additional_feature("new_feature", 0.75)
        
        # Original should be unchanged
        assert "new_feature" not in sample_features.features
        
        # New instance should have the feature
        assert updated.get_feature_value("new_feature") == 0.75
        
        # Other features should be preserved
        assert updated.get_feature_value("amount") == 1000.0


class TestFeatureExtractor:
    """Test suite for the FeatureExtractor class."""

    def test_initialization(self, transaction_history):
        """Test initializing with transaction history."""
        extractor = FeatureExtractor(transaction_history)
        assert len(extractor._transaction_history) == 2

    def test_add_transaction_history(self, feature_extractor, valid_transaction):
        """Test adding transaction history."""
        initial_count = len(feature_extractor._transaction_history)
        feature_extractor.add_transaction_history([valid_transaction])
        assert len(feature_extractor._transaction_history) == initial_count + 1

    def test_extract_features_normal_transaction(self, feature_extractor, valid_transaction):
        """Test feature extraction for a normal transaction."""
        features = feature_extractor.extract_features(valid_transaction)
        
        assert isinstance(features, TransactionFeatures)
        assert features.transaction_id == valid_transaction.id
        
        # Check specific features
        assert features.get_feature_value("amount") == 1000.0
        assert features.get_feature_value("is_cross_border") == 0.0  # Same country
        assert features.get_feature_value("unusual_location") == 0.0  # Normal location

    def test_extract_features_high_risk(self, feature_extractor, high_risk_transaction):
        """Test feature extraction for a high-risk transaction."""
        features = feature_extractor.extract_features(high_risk_transaction)
        
        # Check high-risk features
        assert features.get_feature_value("amount") == 50000.0
        assert features.get_feature_value("is_cross_border") == 1.0  # Different countries
        assert features.get_feature_value("unusual_hour") == 1.0  # Unusual hour
        
        # Location would be unusual if not in history
        unusual_location = features.get_feature_value("unusual_location")
        assert unusual_location == 1.0

    def test_calculate_velocity(self, feature_extractor):
        """Test transaction velocity calculation."""
        # All historical transactions are old, velocity should be 0
        velocity = feature_extractor._calculate_velocity("user123", hours=1)
        assert velocity == 0.0
        
        # Add a recent transaction
        recent_tx = Transaction(
            id=uuid4(),
            amount=500.00,
            currency="USD",
            timestamp=datetime.now() - timedelta(minutes=30),
            type=TransactionType.PAYMENT,
            status=TransactionStatus.COMPLETED,
            sender={
                "id": "user123",
                "name": "John Doe",
                "country_code": "US",
                "account_id": "acc123",
                "institution_id": "bank123"
            },
            recipient={
                "id": "user456",
                "name": "Jane Smith",
                "country_code": "US",
                "account_id": "acc456",
                "institution_id": "bank456"
            },
            reference="RECENT-001"
        )
        feature_extractor.add_transaction_history([recent_tx])
        
        # Recent transaction should be counted
        velocity = feature_extractor._calculate_velocity("user123", hours=1)
        assert velocity == 1.0


class TestFraudDetectionModel:
    """Test suite for the FraudDetectionModel class."""

    def test_predict_normal_transaction(self, sample_features):
        """Test prediction for a normal transaction."""
        model = FraudDetectionModel()
        prediction = model.predict(sample_features)
        
        assert isinstance(prediction, FraudPrediction)
        assert prediction.transaction_id == str(sample_features.transaction_id)
        assert prediction.fraud_probability < 0.5  # Low risk
        assert not prediction.is_fraudulent

    def test_predict_high_risk_transaction(self, high_risk_features):
        """Test prediction for a high-risk transaction."""
        model = FraudDetectionModel()
        prediction = model.predict(high_risk_features)
        
        assert prediction.fraud_probability > 0.7  # High risk
        assert prediction.is_fraudulent
        assert "high fraud risk" in prediction.explanation.lower()

    def test_normalize_feature(self):
        """Test feature normalization."""
        model = FraudDetectionModel()
        
        # Amount normalization
        amount_norm = model._normalize_feature("amount", 50000.0)
        assert 0.0 <= amount_norm <= 1.0
        
        # Binary feature normalization
        binary_norm = model._normalize_feature("is_cross_border", 1.0)
        assert binary_norm == 1.0
        
        # Velocity normalization
        velocity_norm = model._normalize_feature("transaction_velocity_1h", 15.0)
        assert velocity_norm == 1.0  # Capped at 1.0

    def test_generate_explanation(self):
        """Test explanation generation."""
        model = FraudDetectionModel()
        
        # Low risk explanation
        low_risk_explanation = model._generate_explanation({
            "amount": 100.0,
            "is_cross_border": 0.0,
            "unusual_location": 0.0,
            "transaction_velocity_1h": 1.0
        }, 0.2)
        assert "legitimate" in low_risk_explanation.lower()
        
        # High risk explanation
        high_risk_explanation = model._generate_explanation({
            "amount": 50000.0,
            "is_cross_border": 1.0,
            "unusual_location": 1.0,
            "transaction_velocity_1h": 5.0,
            "unusual_hour": 1.0
        }, 0.8)
        assert "high fraud risk" in high_risk_explanation.lower()
        assert "unusual" in high_risk_explanation.lower()


class TestFraudDetectionService:
    """Test suite for the FraudDetectionService class."""

    def test_initialization(self):
        """Test service initialization."""
        service = FraudDetectionService()
        assert service._model is not None
        assert service._feature_extractor is not None
        assert service._predictions == {}

    @patch.object(FeatureExtractor, 'extract_features')
    @patch.object(FraudDetectionModel, 'predict')
    def test_process_transaction(self, mock_predict, mock_extract, valid_transaction, sample_features):
        """Test processing a transaction."""
        # Setup mocks
        mock_extract.return_value = sample_features
        mock_prediction = MagicMock()
        mock_prediction.is_fraudulent = False
        mock_prediction.fraud_probability = 0.2
        mock_predict.return_value = mock_prediction
        
        # Create service and process transaction
        service = FraudDetectionService()
        result = service.process_transaction(valid_transaction)
        
        # Verify mocks were called
        mock_extract.assert_called_once_with(valid_transaction)
        mock_predict.assert_called_once_with(sample_features)
        
        # Verify result
        assert result == mock_prediction
        assert str(valid_transaction.id) in service._predictions
        assert service._predictions[str(valid_transaction.id)] == mock_prediction

    def test_get_prediction(self):
        """Test retrieving a previous prediction."""
        service = FraudDetectionService()
        
        # No predictions yet
        assert service.get_prediction("non-existent") is None
        
        # Add a prediction
        tx_id = str(uuid4())
        mock_prediction = MagicMock()
        service._predictions[tx_id] = mock_prediction
        
        # Should retrieve the prediction
        assert service.get_prediction(tx_id) == mock_prediction

    def test_update_transaction_history(self, transaction_history):
        """Test updating transaction history."""
        feature_extractor = MagicMock()
        service = FraudDetectionService(feature_extractor=feature_extractor)
        
        service.update_transaction_history(transaction_history)
        
        # Verify feature extractor was updated
        feature_extractor.add_transaction_history.assert_called_once_with(transaction_history)

    def test_should_block_transaction(self):
        """Test transaction blocking decision."""
        service = FraudDetectionService()
        
        # Create predictions with different risk levels
        low_risk = MagicMock()
        low_risk.fraud_probability = 0.3
        low_risk.confidence = 0.8
        
        medium_risk = MagicMock()
        medium_risk.fraud_probability = 0.75
        medium_risk.confidence = 0.6  # Low confidence
        
        high_risk = MagicMock()
        high_risk.fraud_probability = 0.75
        high_risk.confidence = 0.9  # High confidence
        
        very_high_risk = MagicMock()
        very_high_risk.fraud_probability = 0.95
        very_high_risk.confidence = 0.7
        
        # Test blocking decisions
        assert not service.should_block_transaction(low_risk)
        assert not service.should_block_transaction(medium_risk)  # Not confident enough
        assert service.should_block_transaction(high_risk)
        assert service.should_block_transaction(very_high_risk) 