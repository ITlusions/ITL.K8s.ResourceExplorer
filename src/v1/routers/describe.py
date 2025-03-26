from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException
from v1.models.models import ResourceDetail
from v1.controllers.resourceexplorer.describe import (
    describe_resource as controller_describe_resource,
)

router = APIRouter(prefix="/describe", tags=["Describe Resources"])

@router.get("/{namespace}/{resource_type}/{resource_name}", response_model=ResourceDetail)
async def describe_resource(namespace: str, resource_type: str, resource_name: str):
    try:
        resource_detail = await controller_describe_resource(namespace, resource_type, resource_name)
        return resource_detail
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)