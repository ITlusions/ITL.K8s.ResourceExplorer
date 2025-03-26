import os
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any
from datetime import datetime
from base.utils import mask_secrets

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
        return mask_secrets(value)
    
class NamespaceResources(BaseModel):
    """Represents resources grouped by namespace."""
    namespace: str
    resources: Dict[str, List[str]]  # Generalized structure for different resource types

class S3Account(BaseModel):
    access_key: str
    secret_key: str
    
class S3AccountRequest(BaseModel):
    access_key: str
    secret_key: str
    endpoint_url: str = None
    secure_flag: bool = True
    cert_check: bool = True