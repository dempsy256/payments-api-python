import random
import string

def validate_amount(amount) -> bool:
    # Must be an exact integer and >= 1 (no floats/decimals allowed for pence/cents)
    return isinstance(amount, int) and amount >= 1

def validate_currency(currency) -> bool:
    # Must be 3 characters and all letters (e.g., USD, EUR, GBP)
    return isinstance(currency, str) and len(currency) == 3 and currency.isalpha()

def validate_email(email) -> bool:
    # Must have exactly one @ symbol
    if not isinstance(email, str) or email.count("@") != 1:
        return False

    # Split by @ and check both parts exist
    parts = email.split("@")
    local_part = parts[0]
    domain_part = parts[1]

    # Local part must exist and domain must have at least one "."
    if not (len(local_part) > 0 and "." in domain_part):
        return False

    # Domain must have content before and after the dot
    domain_parts = domain_part.split(".")
    return all(len(part) > 0 for part in domain_parts)

def generate_id(prefix: str) -> str:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{prefix}_{suffix}"