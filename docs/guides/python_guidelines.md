# Python Development Guidelines

## 7 Rules for Maintainable Python Code

This document outlines the core principles for writing maintainable Python code in the SecureFinStack project. Adherence to these guidelines will help ensure our codebase remains clean, testable, and easy to maintain over time.

### 1. Write As Many Unit Tests As Practical

- Aim for 90%+ code coverage for all new code
- Use pytest as the primary testing framework
- Write tests before implementing functionality (TDD approach)
- Test edge cases and failure scenarios thoroughly
- Use mocking to isolate unit tests from external dependencies
- Run tests automatically in CI/CD pipeline

```python
# Example of a testable function
def calculate_risk_score(transaction_data: dict) -> float:
    """Calculate risk score based on transaction data."""
    if not transaction_data:
        return 0.0
    
    # Calculate risk score
    score = 0.0
    if transaction_data.get("amount", 0) > 10000:
        score += 0.5
    if transaction_data.get("country") not in AUTHORIZED_COUNTRIES:
        score += 0.7
    
    return min(score, 1.0)

# Example test
def test_calculate_risk_score():
    # Test with empty data
    assert calculate_risk_score({}) == 0.0
    
    # Test with high amount
    assert calculate_risk_score({"amount": 20000, "country": "US"}) == 0.5
    
    # Test with unauthorized country
    assert calculate_risk_score({"amount": 100, "country": "XY"}) == 0.7
    
    # Test with both risk factors
    assert calculate_risk_score({"amount": 20000, "country": "XY"}) == 1.0
```

### 2. Use Type Annotations and Static Type Checking

- Add type hints to all function signatures and variable declarations
- Use `Optional` and `Union` types appropriately
- Implement generic types when applicable
- Run MyPy as part of the CI/CD pipeline
- Use typed collections: `List`, `Dict`, `Set`, etc.
- Document complex types with docstrings

```python
from typing import Dict, List, Optional, Union, TypedDict

class TransactionData(TypedDict):
    amount: float
    country: str
    timestamp: str
    user_id: Optional[str]

def process_transactions(
    transactions: List[TransactionData],
    threshold: Optional[float] = None
) -> Dict[str, List[TransactionData]]:
    """
    Process and categorize transactions.
    
    Args:
        transactions: List of transaction data
        threshold: Optional filtering threshold
        
    Returns:
        Dictionary with categorized transactions
    """
    result: Dict[str, List[TransactionData]] = {
        "high_risk": [],
        "medium_risk": [],
        "low_risk": []
    }
    
    # Implementation
    
    return result
```

### 3. Use Auto-Formatting Tools

- Use Black for consistent code formatting
- Apply isort for organized imports
- Use flake8 for style checking
- Add pre-commit hooks for automatic formatting
- Configure IDE to format on save
- Maintain consistent formatting in the entire codebase

```bash
# Example pre-commit configuration (pre-commit-config.yaml)
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: ["--profile", "black"]

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8
        additional_dependencies: [flake8-docstrings]
```

### 4. Minimize Inheritance, Maximize Composition

- Prefer composition over inheritance
- Use dependency injection for better testability
- Utilize mixins for shared functionality when necessary
- Keep inheritance hierarchies shallow (maximum 2-3 levels)
- Create small, focused classes with single responsibilities
- Use interfaces (Protocols) to define behavior

```python
# Avoid deep inheritance hierarchies
# Instead of:
class BaseHandler:
    # ...

class APIHandler(BaseHandler):
    # ...

class TransactionAPIHandler(APIHandler):
    # ...

class PaymentTransactionAPIHandler(TransactionAPIHandler):
    # ...

# Better approach using composition:
class Logger:
    def log(self, message: str) -> None:
        # Logging implementation

class Validator:
    def validate(self, data: dict) -> bool:
        # Validation implementation

class TransactionProcessor:
    def __init__(self, logger: Logger, validator: Validator):
        self.logger = logger
        self.validator = validator
    
    def process(self, transaction: dict) -> dict:
        self.logger.log(f"Processing transaction: {transaction['id']}")
        if not self.validator.validate(transaction):
            raise ValueError("Invalid transaction")
        # Process transaction
        return {"status": "processed", "transaction_id": transaction["id"]}
```

### 5. Choose Immutability Whenever Possible

- Use immutable data structures (tuples, frozensets)
- Make classes immutable with frozen dataclasses
- Avoid modifying function parameters
- Return new objects instead of modifying existing ones
- Use constants for configuration values
- Document where mutability is necessary

```python
from dataclasses import dataclass
from typing import FrozenSet, Tuple
from datetime import datetime

# Immutable constants
MAX_TRANSACTION_AMOUNT = 1_000_000
RESTRICTED_COUNTRIES = frozenset(["XY", "ZZ"])

@dataclass(frozen=True)
class Transaction:
    id: str
    amount: float
    timestamp: datetime
    country: str
    
    def with_updated_amount(self, new_amount: float) -> "Transaction":
        """Return a new Transaction with the updated amount."""
        return Transaction(
            id=self.id,
            amount=new_amount,
            timestamp=self.timestamp,
            country=self.country
        )

# Immutable collections
def get_high_risk_countries() -> Tuple[str, ...]:
    return ("XY", "ZZ", "ABC")
```

### 6. Choose Pure Functions Whenever Possible

- Write functions without side effects
- Ensure functions return the same output for the same input
- Separate pure logic from I/O operations
- Use dependency injection for external resources
- Document when functions have side effects
- Group impure operations at boundaries of the system

```python
# Pure function
def calculate_fee(amount: float, country: str) -> float:
    """Calculate transaction fee based on amount and country."""
    base_fee = amount * 0.01
    if country in ["US", "CA"]:
        return base_fee
    return base_fee * 1.5

# Impure function (clearly documented)
def save_transaction(
    transaction: Transaction,
    database: Database
) -> None:
    """
    Save transaction to database.
    
    Note: This function has side effects - it modifies the database.
    """
    database.insert(
        "transactions",
        {
            "id": transaction.id,
            "amount": transaction.amount,
            "timestamp": transaction.timestamp.isoformat(),
            "country": transaction.country
        }
    )
```

### 7. Break Clean Code Rules Only for Good Reasons

- Document any deviations from coding standards
- Explain the reasoning behind rule violations
- Use linter disable comments sparingly and with explanations
- Continuously reassess technical debt
- Refactor code that breaks rules when possible
- Create a process for reviewing rule exceptions

```python
# Example of a documented exception
# flake8: noqa: C901
def complex_regulatory_calculation(data: Dict[str, Any]) -> float:
    """
    Calculate regulatory capital requirements.
    
    Note: This function is necessarily complex due to regulatory requirements 
    from Basel III section 4.2. The complexity cannot be reduced without 
    violating compliance requirements.
    
    TODO: Consider refactoring if regulatory requirements change.
    """
    # Complex implementation
    pass

# Another example
def legacy_integration_adapter(input_data: dict) -> dict:
    """
    Adapt modern data format to legacy system format.
    
    Note: This function uses non-standard naming to match the legacy system API.
    Do not use this naming pattern elsewhere in the codebase.
    """
    # Non-standard naming to match legacy API
    return {
        "Tx_ID": input_data["transaction_id"],  # noqa: N815
        "AMT": input_data["amount"],  # noqa: N815
        "CST_ID": input_data["customer_id"]  # noqa: N815
    }
```

## Implementation in SecureFinStack

These rules are enforced through:

1. **CI/CD Pipeline**: Automated checks for tests, types, and formatting
2. **Code Reviews**: Verification of adherence to guidelines
3. **Development Environment**: Pre-configured tools and IDE settings
4. **Documentation**: Comprehensive guidelines and examples
5. **Training**: Regular training sessions on best practices

## Additional Resources

- [MyPy Documentation](http://mypy-lang.org/)
- [Black Documentation](https://black.readthedocs.io/en/stable/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Functional Programming in Python](https://docs.python.org/3/howto/functional.html) 