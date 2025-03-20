"""
Fraud Detection Service

This module provides machine learning-based fraud detection capabilities
for financial transactions, following clean code principles.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, FrozenSet, List, Optional, Set, Tuple, TypedDict, Union
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field

from ..transactions.models import Transaction, RiskLevel, TransactionStatus

# Configure logging
logger = logging.getLogger(__name__)

# Feature extraction constants
VELOCITY_TIMEFRAMES: Tuple[int, ...] = (1, 24, 168)  # 1 hour, 24 hours, 1 week in hours
AMOUNT_PERCENTILES: Tuple[float, ...] = (0.25, 0.5, 0.75, 0.95, 0.99)
GEO_DISTANCE_THRESHOLDS: Tuple[int, ...] = (100, 1000, 5000)  # in km
UNUSUAL_HOURS: FrozenSet[int] = frozenset(range(0, 6))  # Midnight to 6 AM

# Model feature names
FEATURE_NAMES: Tuple[str, ...] = (
    "amount",
    "amount_percentile",
    "is_cross_border",
    "transaction_velocity_1h",
    "transaction_velocity_24h",
    "transaction_velocity_7d",
    "unusual_hour",
    "unusual_location",
    "unusual_merchant_category",
    "recipient_risk_score",
    "transaction_risk_score",
)


class FraudPrediction(BaseModel):
    """Fraud prediction result with explanation."""
    transaction_id: str
    fraud_probability: float
    is_fraudulent: bool
    confidence: float
    timestamp: datetime
    feature_importance: Dict[str, float]
    explanation: str


@dataclass(frozen=True)
class TransactionFeatures:
    """Immutable container for transaction features used in fraud detection."""
    features: Dict[str, float]
    transaction_id: UUID
    timestamp: datetime
    
    def to_array(self) -> np.ndarray:
        """Convert features to numpy array for model prediction."""
        return np.array([
            self.features.get(feature, 0.0) for feature in FEATURE_NAMES
        ], dtype=np.float32)
    
    def get_feature_value(self, feature_name: str) -> float:
        """Get value for a specific feature."""
        return self.features.get(feature_name, 0.0)
    
    def with_additional_feature(self, name: str, value: float) -> "TransactionFeatures":
        """Return a new instance with an additional feature."""
        new_features = dict(self.features)
        new_features[name] = value
        return TransactionFeatures(
            features=new_features,
            transaction_id=self.transaction_id,
            timestamp=self.timestamp
        )


class FeatureExtractor:
    """Extract features from transactions for fraud detection."""
    
    def __init__(self, transaction_history: Optional[List[Transaction]] = None):
        """Initialize feature extractor with optional transaction history."""
        self._transaction_history = transaction_history or []
        self._country_risk_scores: Dict[str, float] = {}
        self._account_patterns: Dict[str, Dict] = {}
        
    def add_transaction_history(self, transactions: List[Transaction]) -> None:
        """Add transaction history for context."""
        self._transaction_history.extend(transactions)
        
    def extract_features(self, transaction: Transaction) -> TransactionFeatures:
        """
        Extract features from a transaction for fraud detection.
        
        Args:
            transaction: The transaction to extract features from
            
        Returns:
            TransactionFeatures with extracted features
        """
        features: Dict[str, float] = {}
        
        # Basic transaction features
        features["amount"] = float(transaction.amount)
        features["is_cross_border"] = float(
            transaction.sender["country_code"] != transaction.recipient["country_code"]
        )
        
        # Transaction velocity features
        for hours in VELOCITY_TIMEFRAMES:
            timeframe_key = f"transaction_velocity_{hours}h"
            features[timeframe_key] = self._calculate_velocity(
                transaction.sender["id"], 
                hours=hours
            )
        
        # Time-based features
        tx_hour = transaction.timestamp.hour
        features["unusual_hour"] = float(tx_hour in UNUSUAL_HOURS)
        
        # Amount percentile compared to user history
        features["amount_percentile"] = self._calculate_amount_percentile(
            transaction.sender["id"],
            transaction.amount
        )
        
        # Location and category anomaly
        features["unusual_location"] = self._is_unusual_location(transaction)
        features["unusual_merchant_category"] = 0.0  # Placeholder
        
        # Risk scores
        features["recipient_risk_score"] = self._get_recipient_risk_score(transaction)
        features["transaction_risk_score"] = transaction.risk_score or 0.0
        
        return TransactionFeatures(
            features=features,
            transaction_id=transaction.id,
            timestamp=transaction.timestamp
        )

    def _calculate_velocity(self, user_id: str, hours: int) -> float:
        """
        Calculate transaction velocity for a user within a time window.
        
        Args:
            user_id: User identifier
            hours: Number of hours in the lookback window
            
        Returns:
            Number of transactions in the time window
        """
        if not self._transaction_history:
            return 0.0
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        transactions_in_window = [
            tx for tx in self._transaction_history
            if tx.sender["id"] == user_id and tx.timestamp >= cutoff_time
        ]
        
        return float(len(transactions_in_window))
    
    def _calculate_amount_percentile(self, user_id: str, amount: float) -> float:
        """Calculate the percentile of the transaction amount compared to user history."""
        user_transactions = [
            tx.amount for tx in self._transaction_history
            if tx.sender["id"] == user_id
        ]
        
        if not user_transactions:
            return 0.5  # Default to median if no history
            
        user_transactions.sort()
        count = len(user_transactions)
        
        position = 0
        for i, amt in enumerate(user_transactions):
            if amt >= amount:
                position = i
                break
        
        return position / count if count > 0 else 0.5
    
    def _is_unusual_location(self, transaction: Transaction) -> float:
        """Determine if the transaction location is unusual for the user."""
        # This would use geo-location distance in a real implementation
        # Simplified for demonstration
        user_id = transaction.sender["id"]
        country = transaction.recipient["country_code"]
        
        # Count countries in user history
        country_counts: Dict[str, int] = {}
        for tx in self._transaction_history:
            if tx.sender["id"] == user_id:
                tx_country = tx.recipient["country_code"]
                country_counts[tx_country] = country_counts.get(tx_country, 0) + 1
        
        # If no history or country is common, not unusual
        if not country_counts or country in country_counts:
            return 0.0
            
        return 1.0
    
    def _get_recipient_risk_score(self, transaction: Transaction) -> float:
        """Get risk score for recipient based on history."""
        recipient_id = transaction.recipient["id"]
        
        if not self._transaction_history:
            return 0.0
            
        # Filter transactions for this recipient
        recipient_transactions = [
            tx for tx in self._transaction_history
            if tx.recipient["id"] == recipient_id
        ]
        
        if not recipient_transactions:
            return 0.0
            
        # Calculate average risk score
        avg_risk = sum(
            tx.risk_score or 0.0 for tx in recipient_transactions
        ) / len(recipient_transactions)
        
        return avg_risk


class FraudDetectionModel:
    """
    Machine learning model for fraud detection.
    
    In a real implementation, this would use a trained ML model.
    For demonstration, this uses a rule-based approach.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the fraud detection model.
        
        Args:
            model_path: Optional path to a saved model
        """
        self._feature_importance: Dict[str, float] = {
            "amount": 0.15,
            "is_cross_border": 0.10,
            "transaction_velocity_1h": 0.20,
            "transaction_velocity_24h": 0.10,
            "transaction_velocity_7d": 0.05,
            "unusual_hour": 0.10,
            "unusual_location": 0.15,
            "unusual_merchant_category": 0.05,
            "recipient_risk_score": 0.05,
            "transaction_risk_score": 0.05,
        }
        
    def predict(self, features: TransactionFeatures) -> FraudPrediction:
        """
        Predict if a transaction is fraudulent.
        
        Args:
            features: Transaction features for prediction
            
        Returns:
            FraudPrediction with prediction results
        """
        # Calculate fraud probability using a weighted feature approach
        # In a real implementation, this would use the loaded ML model
        fraud_score = 0.0
        feature_dict = features.features
        
        for feature_name, importance in self._feature_importance.items():
            feature_value = feature_dict.get(feature_name, 0.0)
            normalized_value = self._normalize_feature(feature_name, feature_value)
            fraud_score += normalized_value * importance
        
        # Adjust based on combined risk factors
        if (feature_dict.get("unusual_location", 0) > 0.5 and 
            feature_dict.get("transaction_velocity_1h", 0) > 3.0):
            fraud_score += 0.2
            
        if (feature_dict.get("amount", 0) > 10000 and 
            feature_dict.get("is_cross_border", 0) > 0.5):
            fraud_score += 0.1
            
        # Ensure score is between 0 and 1
        fraud_score = max(0.0, min(1.0, fraud_score))
        
        # Generate explanation
        explanation = self._generate_explanation(feature_dict, fraud_score)
        
        return FraudPrediction(
            transaction_id=str(features.transaction_id),
            fraud_probability=fraud_score,
            is_fraudulent=fraud_score > 0.7,  # Threshold for fraud
            confidence=0.8,  # Placeholder
            timestamp=datetime.now(),
            feature_importance=self._feature_importance,
            explanation=explanation
        )
    
    def _normalize_feature(self, feature_name: str, value: float) -> float:
        """Normalize feature value to [0, 1] range."""
        if feature_name == "amount":
            # Log-scale normalization for amount
            return min(1.0, max(0.0, np.log1p(value) / np.log1p(50000)))
        elif feature_name.startswith("transaction_velocity"):
            # Normalize velocity (0-10 scale)
            return min(1.0, value / 10.0)
        elif feature_name in {"is_cross_border", "unusual_hour", "unusual_location"}:
            # Binary features already normalized
            return value
        else:
            # Default normalization (assume 0-1 range)
            return min(1.0, max(0.0, value))
    
    def _generate_explanation(self, features: Dict[str, float], score: float) -> str:
        """Generate human-readable explanation for fraud prediction."""
        reasons = []
        
        if score > 0.7:
            reasons.append("Transaction shows high fraud risk patterns.")
            
            if features.get("unusual_location", 0) > 0.5:
                reasons.append("Transaction location is unusual for this user.")
                
            if features.get("transaction_velocity_1h", 0) > 3.0:
                reasons.append("Unusually high transaction frequency in the last hour.")
                
            if features.get("amount", 0) > 10000 and features.get("is_cross_border", 0) > 0.5:
                reasons.append("Large cross-border transaction amount.")
                
            if features.get("unusual_hour", 0) > 0.5:
                reasons.append("Transaction occurred during unusual hours.")
        else:
            reasons.append("Transaction appears legitimate.")
            
            if features.get("transaction_velocity_1h", 0) <= 3.0:
                reasons.append("Normal transaction frequency.")
                
            if features.get("unusual_location", 0) <= 0.5:
                reasons.append("Transaction location is normal for this user.")
        
        return " ".join(reasons)


class FraudDetectionService:
    """
    Service for detecting fraudulent transactions.
    
    This service combines feature extraction with model prediction
    to provide fraud detection capabilities.
    """
    
    def __init__(
        self,
        model: Optional[FraudDetectionModel] = None,
        feature_extractor: Optional[FeatureExtractor] = None
    ):
        """
        Initialize the fraud detection service.
        
        Args:
            model: Optional fraud detection model
            feature_extractor: Optional feature extractor
        """
        self._model = model or FraudDetectionModel()
        self._feature_extractor = feature_extractor or FeatureExtractor()
        self._predictions: Dict[str, FraudPrediction] = {}
        
    def process_transaction(self, transaction: Transaction) -> FraudPrediction:
        """
        Process a transaction for fraud detection.
        
        Args:
            transaction: The transaction to process
            
        Returns:
            FraudPrediction with fraud analysis results
        """
        logger.info(f"Processing transaction {transaction.id} for fraud detection")
        
        # Extract features
        features = self._feature_extractor.extract_features(transaction)
        
        # Make prediction
        prediction = self._model.predict(features)
        
        # Store prediction
        self._predictions[str(transaction.id)] = prediction
        
        # Log high-risk predictions
        if prediction.is_fraudulent:
            logger.warning(
                f"Potential fraud detected for transaction {transaction.id} "
                f"with probability {prediction.fraud_probability:.2f}"
            )
        
        return prediction
    
    def get_prediction(self, transaction_id: str) -> Optional[FraudPrediction]:
        """
        Retrieve a previous fraud prediction by transaction ID.
        
        Args:
            transaction_id: The transaction ID to look up
            
        Returns:
            FraudPrediction if found, None otherwise
        """
        return self._predictions.get(transaction_id)
    
    def update_transaction_history(self, transactions: List[Transaction]) -> None:
        """
        Update the transaction history for context.
        
        Args:
            transactions: List of transactions to add to history
        """
        self._feature_extractor.add_transaction_history(transactions)
    
    def should_block_transaction(self, prediction: FraudPrediction) -> bool:
        """
        Determine if a transaction should be blocked based on fraud prediction.
        
        Args:
            prediction: The fraud prediction to evaluate
            
        Returns:
            True if the transaction should be blocked, False otherwise
        """
        # Transactions with high fraud probability should be blocked
        if prediction.fraud_probability > 0.9:
            return True
            
        # Transactions with medium-high fraud probability and high confidence
        if prediction.fraud_probability > 0.7 and prediction.confidence > 0.8:
            return True
            
        return False 