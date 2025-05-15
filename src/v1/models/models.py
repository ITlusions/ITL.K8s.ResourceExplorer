import os
from pydantic import BaseModel, field_validator, Field
from typing import List, Dict, Any, Optional
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

class ConnectionRequest(BaseModel):
    host: str = Field(..., description="The hostname or IP address to connect to.")
    port: int = Field(..., description="The port to connect to.")
    
class CRD(BaseModel):
    name: str
    group: str
    version: str

class CRDItemRequest(BaseModel):
    group: str
    version: str
    plural: str
    namespace: Optional[str] = None
    
class Pod(BaseModel):
    name: str
    status: str

class Service(BaseModel):
    name: str
    type: str

class Deployment(BaseModel):
    name: str
    replicas: Optional[int]

class NamespaceResources(BaseModel):
    namespace: str
    pods: List[Pod]
    services: List[Service]
    deployments: List[Deployment]

class NotFoundResponse(BaseModel):
    detail: str
    
class KubernetesEvent(BaseModel):
    type: str
    name: str
    namespace: Optional[str]
    message: str
    reason: Optional[str]
    timestamp: Optional[str]

class DeleteDeploymentRequest(BaseModel):
    namespace: str
    deployment_name: str

