from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client.exceptions import ApiException
from v1.models.models import ResourceDetail, NotFoundResponse
from v1.controllers.resourceexplorer.describe import (
    get_all_resource_types as controller_get_all_resource_types,
    describe_resource as controller_describe_resource,
    list_resources_grouped_by_namespace as controller_list_resources_grouped_by_namespace
    
)

k8s_resources_router = APIRouter(prefix="/k8s", tags=["K8s Resources"])

@k8s_resources_router.get("/resourcetypes", response_model=dict)
async def list_resource_types():
    """
    API endpoint to list all available resource types in the Kubernetes cluster.
    """
    try:
        return controller_get_all_resource_types()
    except HTTPException as e:
        raise e
    
@k8s_resources_router.get("/{namespace}/{resource_type}/{resource_name}", response_model=ResourceDetail, responses={404: {"model": NotFoundResponse}})
async def get_resource_details(namespace: str, resource_type: str, resource_name: str):
    """
    API endpoint to get details of a specific Kubernetes resource.
    """
    try:
        resource_detail = await controller_describe_resource(namespace, resource_type, resource_name)
        return resource_detail
    except HTTPException as e:
        if e.status_code == 404:
            return JSONResponse(status_code=404, content={"detail": e.detail})
        raise


@k8s_resources_router.get("/resources", response_model=dict)
def get_resources_grouped_by_namespace():
    """
    API endpoint to list all Kubernetes resources grouped by namespace.
    """
    return controller_list_resources_grouped_by_namespace()

@k8s_resources_router.get("/{namespace}/resources", response_model=dict)
async def list_resources_by_namespace(namespace: str):
    """
    API endpoint to list all Kubernetes resources in a specific namespace.
    """
    # Filter resources by the given namespace
    #all_resources = await controller_list_resources_grouped_by_namespace()
    return {"message": "Not implemented yet"}

@k8s_resources_router.get("/{namespace}/ingresses", response_model=dict)
async def list_ingresses(namespace: str):
    """
    API endpoint to list all Ingresses in a specific namespace.
    """
    try:
        # ingresses = await controller_list_ingresses(namespace)
        # return {"namespace": namespace, "ingresses": ingresses}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)


@k8s_resources_router.get("/{namespace}/services", response_model=dict)
async def list_services(namespace: str):
    """
    API endpoint to list all Services in a specific namespace.
    """
    try:
        # services = await controller_list_services(namespace)
        # return {"namespace": namespace, "services": services}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    
@k8s_resources_router.get("/{namespace}/jobs", response_model=dict)
async def list_jobs(namespace: str):
    """
    API endpoint to list all Jobs in a specific namespace.
    """
    try:
        # jobs = await controller_list_jobs(namespace)
        # return {"namespace": namespace, "jobs": jobs}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)


@k8s_resources_router.post("/{namespace}/cronjobs/{cronjob_name}/trigger", response_model=dict)
async def trigger_cronjob(namespace: str, cronjob_name: str):
    """
    API endpoint to manually trigger a Kubernetes CronJob.
    """
    try:
        # result = await controller_trigger_cronjob(namespace, cronjob_name)
        # return {"namespace": namespace, "cronjob_name": cronjob_name, "result": result}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)