import pytest
from src.utils.validators import validate_amount, validate_currency, validate_email, generate_id

def test_validate_amount_returns_true_for_100():
    assert validate_amount(100) is True

def test_validate_amount_returns_false_for_0():
    assert validate_amount(0) is False

# Add boundary tests: 1, -1, 9.99, None, '100'

def test_validate_currency_returns_true_for_usd():
    assert validate_currency("usd") is True

def test_validate_email_returns_true_for_valid_email():
    assert validate_email("alice@example.com") is True

def test_validate_email_returns_false_for_missing_at_symbol():
    assert validate_email("aliceexample.com") is False