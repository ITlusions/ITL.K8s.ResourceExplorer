from fastapi import APIRouter, HTTPException, WebSocket, Query, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from kubernetes.client.exceptions import ApiException
from v1.models.models import ResourceDetail, NotFoundResponse, StorageClass
from v1.controllers.k8s import (
    get_all_resource_types as controller_get_all_resource_types,
    describe_resource as controller_describe_resource,
    list_resources_grouped_by_namespace as controller_list_resources_grouped_by_namespace,
    stream_kubernetes_events as controller_stream_kubernetes_events,
    list_ingresses as controller_list_ingresses,
    list_nodes as controller_list_nodes,
    controller_list_storage_classes,  # Ensure the correct import
    interactive_exec
)
from utils.auth import validate_token

k8s_resources_router = APIRouter(
    prefix="/k8s",
    tags=["K8s Resources"],
    description="This router includes Kubernetes resource management endpoints. "
                "Note: The WebSocket endpoint `/ws/exec` is not visible in the API docs but is functional.",
)

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
    try:
        all_resources = await controller_list_resources_grouped_by_namespace()
        namespace_resources = all_resources.get(namespace, {})
        return {"namespace": namespace, "resources": namespace_resources}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)

@k8s_resources_router.get("/{namespace}/ingresses", response_model=dict)
async def list_ingresses(namespace: str):
    """
    API endpoint to list all Ingresses in a specific namespace.
    """
    try:
        ingresses = await controller_list_ingresses(namespace)
        return {"namespace": namespace, "ingresses": ingresses}
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
    
@k8s_resources_router.get("/jobs", response_model=dict)
async def list_all_jobs():
    """
    API endpoint to list all Jobs in the Kubernetes cluster.
    """
    try:
        # all_jobs = await controller_list_all_jobs()
        # return {"jobs": all_jobs}
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
    
@k8s_resources_router.get("/{namespace}/configmaps", response_model=dict)
async def list_configmaps(namespace: str):
    """
    API endpoint to list all ConfigMaps in a specific namespace.
    """
    try:
        # configmaps = await controller_list_configmaps(namespace)
        # return {"namespace": namespace, "configmaps": configmaps}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)


@k8s_resources_router.get("/{namespace}/secrets", response_model=dict)
async def list_secrets(namespace: str):
    """
    API endpoint to list all Secrets in a specific namespace.
    """
    try:
        # secrets = await controller_list_secrets(namespace)
        # return {"namespace": namespace, "secrets": secrets}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    
@k8s_resources_router.get("/nodes", response_model=dict)
async def list_nodes():
    """
    API endpoint to list all Nodes in the Kubernetes cluster, including their status and resource usage.
    """
    try:
        nodes = await controller_list_nodes()
        return {"nodes": nodes}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)

@k8s_resources_router.get("/nodes/{node_name}", response_model=dict)
async def get_node_details(node_name: str):
    """
    API endpoint to get details of a specific Node in the Kubernetes cluster.
    """
    try:
        # node_details = await controller_get_node_details(node_name)
        # return {"node_name": node_name, "details": node_details}
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)
    
@k8s_resources_router.get("/events", response_class=StreamingResponse)
async def stream_events():
    """
    API endpoint to stream Kubernetes events in real-time.
    """
    try:
    #     return StreamingResponse(controller_stream_kubernetes_events(), media_type="text/event-stream")
    # except HTTPException as e:
    #     raise e
        return {"message": "Not implemented yet"}
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)

@k8s_resources_router.get("/storageclasses", response_model=list[StorageClass])
async def list_storage_classes():
    """
    API endpoint to list all StorageClasses in the Kubernetes cluster.
    """
    try:
        # Call the controller to fetch storage classes
        return await controller_list_storage_classes()
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=e.reason)

@k8s_resources_router.websocket("/ws/exec")
async def exec_websocket(
    websocket: WebSocket,
    namespace: str = Query(...),
    pod_name: str = Query(...),
    container_name: str = Query(...),
    user_info: dict = Depends(validate_token),  # Inject user info from the dependency
):
    """
    WebSocket endpoint to interactively connect to a Kubernetes container.
    Authentication is performed using Entra ID tokens.
    """
    # Accept the WebSocket connection after successful authentication
    await websocket.accept()

    # Log the authenticated user's information (optional)
    print(f"Authenticated user: {user_info.get('preferred_username')}")

    # Call the interactive_exec function to handle the Kubernetes interaction
    await interactive_exec(websocket, namespace, pod_name, container_name)

@k8s_resources_router.get("/ws/exec-docs", response_model=dict)
def websocket_docs():
    """
    Documentation for the WebSocket endpoint to interactively connect to a Kubernetes container.
    """
    return {
        "description": "WebSocket endpoint to interactively connect to a Kubernetes container.",
        "url": "/k8s/ws/exec",
        "parameters": {
            "namespace": "The namespace of the pod.",
            "pod_name": "The name of the pod.",
            "container_name": "The name of the container.",
        },
        "authentication": "Requires a Bearer token in the Authorization header.",
    }