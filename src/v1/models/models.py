from pydantic import BaseModel
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

class NamespaceResources(BaseModel):
    namespace: str
    resources: Dict[str, List[str]]  # Generalized structure for different resource types

