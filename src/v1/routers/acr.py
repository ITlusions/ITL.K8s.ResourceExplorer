from fastapi import APIRouter, HTTPException
from v1.models.acr import ACRCopyRequest, ACRCopyResponse, ACRListRequest, ACRListResponse
from v1.controllers.acr import copy_acr_image_with_credentials, list_acr_repositories_and_images

router = APIRouter(prefix="/acr", tags=["ACR"])

@router.post("/copy", response_model=ACRCopyResponse)
def copy_acr_image_with_credentials_endpoint(request: ACRCopyRequest):
    """
    API endpoint to copy a Docker image from one Azure Container Registry (ACR) to another using different credentials.
    """
    try:
        return copy_acr_image_with_credentials(
            source_registry_url=request.source_registry_url,
            source_repository=request.source_repository,
            source_image_tag=request.source_image_tag,
            source_client_id=request.source_client_id,
            source_client_secret=request.source_client_secret,
            source_tenant_id=request.source_tenant_id,
            destination_registry_url=request.destination_registry_url,
            destination_repository=request.destination_repository,
            destination_client_id=request.destination_client_id,
            destination_client_secret=request.destination_client_secret,
            destination_tenant_id=request.destination_tenant_id,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list", response_model=ACRListResponse)
def list_acr_repositories_and_images_endpoint(request: ACRListRequest):
    """
    API endpoint to list repositories and images in an Azure Container Registry (ACR).
    """
    try:
        return list_acr_repositories_and_images(
            registry_url=request.registry_url,
            client_id=request.client_id,
            client_secret=request.client_secret,
            tenant_id=request.tenant_id,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))