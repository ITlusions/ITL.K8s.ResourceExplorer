import os
from typing import Dict, Any

def is_masking_enabled() -> bool:
    """
    Helper function to determine if masking is enabled.
    """
    return os.getenv("ENABLE_MASKING", "True").lower() in ("true", "1", "yes")

def mask_secrets(value: Dict[str, Any]) -> Dict[str, Any]:
    """
    Masks sensitive information in a dictionary.
    """
    if not is_masking_enabled():
        return value
    if isinstance(value, dict):
        for key in value:
            if any(sensitive in key.lower() for sensitive in ["secret", "token", "password"]):
                value[key] = "***REDACTED***"
    return value