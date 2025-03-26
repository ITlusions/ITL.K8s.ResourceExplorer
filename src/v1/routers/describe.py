from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException
from models import ResourceDetail  # Import from models.py
from v1.controllers.resourceexplorer.describe import (
    describe_resource as controller_describe_resource,
)

router = APIRouter(prefix="/describe", tags=["Describe Resources"])

@router.get("/{namespace}/{resource_type}/{resource_name}", response_model=ResourceDetail)
async def describe_resource(namespace: str, resource_type: str, resource_name: str):
    try:
        resource_detail = controller_describe_resource(namespace, resource_type, resource_name)
        return resource_detail
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)