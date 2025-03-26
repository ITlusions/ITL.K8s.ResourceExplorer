import os
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any
from datetime import datetime

class ResourceMetadata(BaseModel):
    name: str
    namespace: str
    creation_timestamp: datetime

class ResourceDetail(BaseModel):
    metadata: ResourceMetadata
    spec: Dict[str, Any]
    status: Dict[str, Any]

    @classmethod
    def is_masking_enabled(cls) -> bool:
        """Helper method to determine if masking is enabled."""
        return os.getenv("ENABLE_MASKING", "True").lower() in ("true", "1", "yes")

    @field_validator("spec", "status", mode="before")
    def mask_secrets(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not cls.is_masking_enabled():
            return value
        if isinstance(value, dict):
            for key in value:
                if any(sensitive in key.lower() for sensitive in ["secret", "token", "password"]):
                    value[key] = "***REDACTED***"
        return value

class NamespaceResources(BaseModel):
    """Represents resources grouped by namespace."""
    namespace: str
    resources: Dict[str, List[str]]  # Generalized structure for different resource types

