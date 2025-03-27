from fastapi import APIRouter, HTTPException
from kubernetes.client.exceptions import ApiException
from v1.models.models import ResourceDetail
from v1.controllers.resourceexplorer.describe import (
    describe_resource as controller_describe_resource,
    list_resources_grouped_by_namespace as controller_list_resources_grouped_by_namespace
)

k8s_resources_router = APIRouter(prefix="/k8s", tags=["K8s Resources"])

@k8s_resources_router.get("/{namespace}/{resource_type}/{resource_name}", response_model=ResourceDetail)
async def get_resource_details(namespace: str, resource_type: str, resource_name: str):
    """
    API endpoint to get details of a specific Kubernetes resource.
    """
    try:
        resource_detail = await controller_describe_resource(namespace, resource_type, resource_name)
        return resource_detail
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)


@k8s_resources_router.get("/resources", response_model=dict)
def get_resources_grouped_by_namespace():
    """
    API endpoint to list all Kubernetes resources grouped by namespace.
    """
    return controller_list_resources_grouped_by_namespace()