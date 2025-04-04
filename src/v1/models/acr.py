from pydantic import BaseModel
from typing import List, Dict

class ACRCopyRequest(BaseModel):
    source_registry_url: str
    source_repository: str
    source_image_tag: str
    source_client_id: str
    source_client_secret: str
    source_tenant_id: str
    destination_registry_url: str
    destination_repository: str
    destination_client_id: str
    destination_client_secret: str
    destination_tenant_id: str

class ACRCopyResponse(BaseModel):
    source: dict
    destination: dict

class ACRListRequest(BaseModel):
    registry_url: str
    client_id: str
    client_secret: str
    tenant_id: str

class ACRListResponse(BaseModel):
    registry_url: str
    repositories: Dict[str, List[str]] 