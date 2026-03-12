import random
import string

def validate_amount(amount) -> bool:
    # Must be an exact integer and >= 1 (no floats/decimals allowed for pence/cents)
    return isinstance(amount, int) and amount >= 1

def validate_currency(currency) -> bool:
    return isinstance(currency, str) and len(currency) == 3

def validate_email(email) -> bool:
    return isinstance(email, str) and "@" in email and "." in email

def generate_id(prefix: str) -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{prefix}_{suffix}"