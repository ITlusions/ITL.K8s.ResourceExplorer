from pydantic import BaseModel, Field, HttpUrl, SecretStr, validator
from typing import List, Dict, Optional

class ACRCopyRequest(BaseModel):
    source_registry_url: str = Field(..., description="URL of the source container registry")
    source_repository: str = Field(..., description="Name of the source repository")
    source_image_tag: str = Field(..., description="Tag of the source image")
    source_client_id: str = Field(..., description="Client ID for the source registry authentication")
    source_client_secret: SecretStr = Field(..., description="Client secret for the source registry authentication")
    source_tenant_id: str = Field(..., description="Tenant ID for the source registry authentication")
    destination_registry_url: HttpUrl = Field(..., description="URL of the destination container registry")
    destination_repository: str = Field(..., description="Name of the destination repository")
    destination_client_id: str = Field(..., description="Client ID for the destination registry authentication")
    destination_client_secret: SecretStr = Field(..., description="Client secret for the destination registry authentication")
    destination_tenant_id: str = Field(..., description="Tenant ID for the destination registry authentication")

    @validator("source_repository", "destination_repository")
    def validate_repository_name(cls, value):
        if "/" in value:
            raise ValueError("Repository name cannot contain slashes")
        return value

class ACRCopyResponse(BaseModel):
    source: Dict[str, str] = Field(..., description="Details of the source image")
    destination: Dict[str, str] = Field(..., description="Details of the destination image")
    status: str = Field(..., description="Status of the copy operation (e.g., success, failure)")
    message: Optional[str] = Field(None, description="Additional information about the operation")

class ACRListRequest(BaseModel):
    registry_url: str = Field(..., description="URL of the container registry")
    client_id: str = Field(..., description="Client ID for the registry authentication")
    client_secret: SecretStr = Field(..., description="Client secret for the registry authentication")
    tenant_id: str = Field(..., description="Tenant ID for the registry authentication")
    include_tags: Optional[bool] = Field(False, description="Whether to include image tags in the response")

class ACRListResponse(BaseModel):
    registry_url: str = Field(..., description="URL of the container registry")
    repositories: Dict[str, List[str]] = Field(..., description="Mapping of repositories to their image tags")
    total_repositories: int = Field(..., description="Total number of repositories in the registry")

    @validator("total_repositories", pre=True, always=True)
    def calculate_total_repositories(cls, value, values):
        if "repositories" in values:
            return len(values["repositories"])
        return 0

class ACRAuthRequest(BaseModel):
    registry_url: str = Field(..., description="URL of the container registry")
    token_username: Optional[str] = Field(None, description="Username for token-based authentication")
    token_password: Optional[SecretStr] = Field(None, description="Password for token-based authentication")
    client_id: Optional[str] = Field(None, description="Client ID for OAuth-based authentication")
    client_secret: Optional[SecretStr] = Field(None, description="Client secret for OAuth-based authentication")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for OAuth-based authentication")

    @validator("token_username", "token_password", "client_id", "client_secret", "tenant_id", pre=True, always=True)
    def validate_auth_fields(cls, value, field):
        if not value and field.name in ["token_username", "token_password"]:
            raise ValueError(f"{field.name} is required for token-based authentication")
        if not value and field.name in ["client_id", "client_secret", "tenant_id"]:
            raise ValueError(f"{field.name} is required for OAuth-based authentication")
        return value


class ACRAuthResponse(BaseModel):
    registry_url: str = Field(..., description="URL of the container registry")
    repositories: Dict[str, List[str]] = Field(..., description="Mapping of repository names to their image tags")
    total_repositories: int = Field(..., description="Total number of repositories in the registry")
    authentication_status: str = Field(..., description="Status of the authentication process (e.g., success, failure)")
    message: Optional[str] = Field(None, description="Additional information about the authentication process")

    @validator("total_repositories", pre=True, always=True)
    def calculate_total_repositories(cls, value, values):
        if "repositories" in values:
            return len(values["repositories"])
        return 0