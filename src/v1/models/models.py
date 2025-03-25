from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ResourceMetadata(BaseModel):
    name: str
    namespace: str
    creationTimestamp: str


class ResourceSpec(BaseModel):
    spec: Dict[str, Any]


class ResourceStatus(BaseModel):
    status: Dict[str, Any]


class ResourceDetail(BaseModel):
    metadata: ResourceMetadata
    spec: ResourceSpec
    status: ResourceStatus


class NamespaceResources(BaseModel):
    namespace: str
    pods: List[str]
    services: List[str]
    deployments: List[str]
