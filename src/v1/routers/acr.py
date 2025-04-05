from fastapi import APIRouter, HTTPException
from v1.models.acr import ACRCopyRequest, ACRCopyResponse, ACRListRequest, ACRListResponse
from v1.controllers.acr import list_acr_repositories, copy_acr_image

router = APIRouter(prefix="/acr", tags=["ACR"])


@router.post("/list", response_model=ACRListResponse)
def list_repositories(request: ACRListRequest):
    """
    List repositories and their tags in an Azure Container Registry.
    """
    try:
        repositories = list_acr_repositories(
            subscription_id=request.subscription_id,
            registry_name=request.registry_name,
        )
        return {
            "registry_name": request.registry_name,
            "repositories": repositories,
            "total_repositories": len(repositories),
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copy", response_model=ACRCopyResponse)
def copy_image(request: ACRCopyRequest):
    """
    Copy an image from one Azure Container Registry to another.
    """
    try:
        return copy_acr_image(
            subscription_id=request.subscription_id,
            source_registry=request.source_registry,
            source_repository=request.source_repository,
            source_image_tag=request.source_image_tag,
            destination_registry=request.destination_registry,
            destination_repository=request.destination_repository,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))