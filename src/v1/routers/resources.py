from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from v1.controllers.resourceexplorer.controller import (
    get_all_namespaces as controller_get_namespaces,
    get_all_secrets as controller_get_secrets,
    delete_deployment as controller_delete_deployment,
    delete_resource as controller_delete_resource
)
from v1.models.models import DeleteDeploymentRequest, DeleteResourceRequest

router = APIRouter()

@router.get("/get-secrets")
async def get_secrets():
    try:
        return controller_get_secrets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-namespaces")
async def get_namespaces():
    try:
        return controller_get_namespaces()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/deployments", tags=["Deployments"])
async def delete_k8s_deployment(request: DeleteDeploymentRequest):
    """
    Delete a Kubernetes deployment.
    """
    try:
        result = controller_delete_deployment(request.namespace, request.deployment_name)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/resources", tags=["Resources"])
async def delete_k8s_resource(request: DeleteResourceRequest):
    """
    Delete a Kubernetes resource (Deployment, StatefulSet, ReplicaSet, Pod, PersistentVolume, PersistentVolumeClaim, Namespace).

    Args:
        request (DeleteResourceRequest): The request body containing namespace, resource name, and resource type.

    Returns:
        dict: A success message and details of the deletion.
    """
    try:
        result = controller_delete_resource(request.namespace, request.resource_name, request.resource_type)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

