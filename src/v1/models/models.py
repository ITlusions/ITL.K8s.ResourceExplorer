from pydantic import BaseModel, validator, field_validator
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
    
    @field_validator("spec", "status", mode="before")
    def mask_secrets(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        """Truncates secret values in spec and status fields."""
        if isinstance(value, dict):
            for key in value:
                if "secret" in key.lower() or "token" in key.lower() or "password" in key.lower():
                    value[key] = "***REDACTED***"
        return value

class NamespaceResources(BaseModel):
    """Represents resources grouped by namespace."""
    namespace: str
    resources: Dict[str, List[str]]  # Generalized structure for different resource types

