from pydantic import BaseModel, Field
from typing import List, Dict


class ACRCopyRequest(BaseModel):
    subscription_id: str = Field(..., description="Azure subscription ID")
    source_registry: str = Field(..., description="Name of the source container registry")
    source_repository: str = Field(..., description="Name of the source repository")
    source_image_tag: str = Field(..., description="Tag of the source image")
    destination_registry: str = Field(..., description="Name of the destination container registry")
    destination_repository: str = Field(..., description="Name of the destination repository")


class ACRCopyResponse(BaseModel):
    source: Dict[str, str] = Field(..., description="Details of the source image")
    destination: Dict[str, str] = Field(..., description="Details of the destination image")
    status: str = Field(..., description="Status of the copy operation (e.g., success, failure)")
    message: str = Field(..., description="Additional information about the operation")


class ACRListRequest(BaseModel):
    subscription_id: str = Field(..., description="Azure subscription ID")
    registry_name: str = Field(..., description="Name of the container registry")


class ACRListResponse(BaseModel):
    registry_name: str = Field(..., description="Name of the container registry")
    repositories: Dict[str, List[str]] = Field(..., description="Mapping of repositories to their image tags")
    total_repositories: int = Field(..., description="Total number of repositories in the registry")