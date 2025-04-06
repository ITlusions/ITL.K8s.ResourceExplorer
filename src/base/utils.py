import os
from typing import Dict, Any

def is_masking_enabled() -> bool:
    """
    Helper function to determine if masking is enabled.
    """
    return os.getenv("ENABLE_MASKING", "True").lower() in ("true", "1", "yes")

def mask_secrets(value: Dict[str, Any]) -> Dict[str, Any]:
    """
    Masks sensitive information in a dictionary, including nested dictionaries.
    """
    if not is_masking_enabled():
        return value

    if isinstance(value, dict):
        for key in value:
            # Check if the key contains sensitive keywords
            if any(sensitive in key.lower() for sensitive in ["secret", "token", "password", "tls", "auth", "PrivateKey"]):
                value[key] = "***REDACTED***"
            elif isinstance(value[key], dict):
                # Recursively mask nested dictionaries
                value[key] = mask_secrets(value[key])
            elif isinstance(value[key], list):
                # Recursively mask lists of dictionaries
                value[key] = [mask_secrets(item) if isinstance(item, dict) else item for item in value[key]]
    return value