from fastapi import HTTPException, WebSocket
from kubernetes import client, watch, config, stream
from kubernetes.client.exceptions import ApiException
from base.k8s_config import load_k8s_config

import asyncio
from typing import Optional
from v1.models.models import PersistentVolume, PersistentVolumeClaim

# Load Kubernetes Configurations
load_k8s_config()

core_v1_api = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
apis_api = client.ApisApi()
networking_v1_api = client.NetworkingV1Api()
storage_v1_api = client.StorageV1Api()

def get_all_resource_types():
    """
    Fetch all available resource types in the Kubernetes cluster.
    """
    try:
        # Fetch core API resources
        core_resources = core_v1_api.get_api_resources()
        core_resource_types = [
            {"name": resource.name, "kind": resource.kind, "namespaced": resource.namespaced}
            for resource in core_resources.resources
        ]

        # Fetch resources from all API groups
        api_groups = apis_api.get_api_versions()
        group_resource_types = []
        for group in api_groups.groups:
            for version in group.versions:
                group_version = f"{group.name}/{version.version}" if group.name else version.version
                try:
                    group_resources = client.ApiClient().call_api(
                        f"/apis/{group_version}", "GET", response_type="V1APIResourceList"
                    )
                    group_resource_types.extend([
                        {
                            "name": resource.name,
                            "kind": resource.kind,
                            "namespaced": resource.namespaced,
                            "groupVersion": group_version,
                        }
                        for resource in group_resources.resources
                    ])
                except Exception:
                    continue

        # Combine core and group resources
        all_resource_types = core_resource_types + group_resource_types

        return {"resource_types": all_resource_types}

    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resource types: {str(e)}")

async def describe_resource(namespace: str, resource_type: str, resource_name: str):
    try:
        if resource_type == "pod":
            resource = core_v1_api.read_namespaced_pod(name=resource_name, namespace=namespace)
        elif resource_type == "service":
            resource = core_v1_api.read_namespaced_service(name=resource_name, namespace=namespace)
        elif resource_type == "deployment":
            resource = apps_v1_api.read_namespaced_deployment(name=resource_name, namespace=namespace)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")

        if not resource:
            raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()} '{resource_name}' not found in namespace '{namespace}'")

        return {
            "metadata": resource.metadata.to_dict(),
            "spec": resource.spec.to_dict(),
            "status": resource.status.to_dict(),
        }
    except ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()} '{resource_name}' not found in namespace '{namespace}'")
        raise HTTPException(status_code=500, detail=f"Error fetching resource: {str(e)}")

async def list_resources_grouped_by_namespace():
    """
    Fetch all resources (pods, services, deployments) grouped by namespace.
    """
    try:
        namespaces = core_v1_api.list_namespace().items
        result = {}

        for ns in namespaces:
            namespace_name = ns.metadata.name

            # Fetch resources in the namespace
            pods = core_v1_api.list_namespaced_pod(namespace=namespace_name).items
            services = core_v1_api.list_namespaced_service(namespace=namespace_name).items
            deployments = apps_v1_api.list_namespaced_deployment(namespace=namespace_name).items

            # Group resources by namespace
            result[namespace_name] = {
                "pods": [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods],
                "services": [{"name": svc.metadata.name, "type": svc.spec.type} for svc in services],
                "deployments": [{"name": dep.metadata.name, "replicas": dep.status.replicas} for dep in deployments],
            }

        return result
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching resources: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def stream_kubernetes_events():
    """
    Stream Kubernetes events in real-time.
    """
    v1 = client.CoreV1Api()
    w = watch.Watch()

    try:
        # Watch events in the cluster
        loop = asyncio.get_event_loop()
        for event in await loop.run_in_executor(None, lambda: w.stream(core_v1_api.list_event_for_all_namespaces, timeout_seconds=5)):
            # Format the event as a Server-Sent Event (SSE)
            event_type = event.get("type", "UNKNOWN")
            event_object = event.get("object", {})
            event_name = getattr(event_object.metadata, "name", "UNKNOWN")
            event_message = getattr(event_object, "message", "No message available")
            yield f"data: {event_type} - {event_name} - {event_message}\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
    finally:
        w.stop()

async def list_ingresses(namespace: str) -> list:
    """
    Retrieves a list of Ingresses in the specified namespace.

    Args:
        namespace (str): The namespace to query for Ingresses.

    Returns:
        list: A list of Ingress objects in the specified namespace.
    """
    try:
        # List Ingresses in the specified namespace
        ingresses = networking_v1_api.list_namespaced_ingress(namespace=namespace)

        # Extract relevant information from the Ingress objects
        ingress_list = [
            {
                "name": ingress.metadata.name,
                "namespace": ingress.metadata.namespace,
                "host": ingress.spec.rules[0].host if ingress.spec.rules else None,
                "paths": [
                    path.path for path in ingress.spec.rules[0].http.paths
                ] if ingress.spec.rules and ingress.spec.rules[0].http else [],
                "creation_timestamp": ingress.metadata.creation_timestamp,
            }
            for ingress in ingresses.items
        ]

        return ingress_list

    except ApiException as e:
        raise ApiException(f"Error retrieving Ingresses in namespace '{namespace}': {e.reason}")

async def list_nodes() -> list:
    """
    Retrieves a list of all Nodes in the Kubernetes cluster, including their status and resource usage.

    Returns:
        list: A list of Node objects with relevant details.
    """
    try:

        # List all nodes in the cluster
        nodes = core_v1_api.list_node()

        # Extract relevant information from the Node objects
        node_list = [
            {
                "name": node.metadata.name,
                "status": "Ready" if any(
                    condition.type == "Ready" and condition.status == "True"
                    for condition in node.status.conditions
                ) else "NotReady",
                "capacity": node.status.capacity,
                "allocatable": node.status.allocatable,
                "labels": node.metadata.labels,
                "creation_timestamp": node.metadata.creation_timestamp,
            }
            for node in nodes.items
        ]

        return node_list

    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error retrieving nodes: {e.reason}")

async def controller_list_storage_classes():
    """
    Controller to list all StorageClasses in the Kubernetes cluster.
    """
    try:
        # Fetch all storage classes
        storage_classes = storage_v1_api.list_storage_class()
        return [
            {
                "name": sc.metadata.name,
                "provisioner": sc.provisioner,
                "reclaim_policy": sc.reclaim_policy,
                "volume_binding_mode": sc.volume_binding_mode,
            }
            for sc in storage_classes.items
        ]
    except client.exceptions.ApiException as e:
        raise ApiException(status=e.status, reason=e.reason)

async def interactive_exec(websocket: WebSocket, namespace: str, pod_name: str, container_name: str):
    """
    Controller to handle interactive WebSocket streaming to a Kubernetes container.
    """
    try:

        # Define the command to start a shell
        exec_command = ["/bin/sh"]

        # Open a WebSocket stream to the Kubernetes API
        resp = stream.stream(
            core_v1_api.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            container=container_name,
            command=exec_command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=True,
            _preload_content=False,  # Disable automatic content processing
        )

        # Accept the WebSocket connection
        await websocket.accept()

        # Read and write data between the client and the Kubernetes pod
        while resp.is_open():
            # Read data from the Kubernetes stream
            if resp.peek_stdout():
                output = resp.read_stdout()
                await websocket.send_text(output)

            if resp.peek_stderr():
                error = resp.read_stderr()
                await websocket.send_text(error)

            # Read data from the WebSocket client
            data = await websocket.receive_text()
            resp.write_stdin(data)

        resp.close()
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))

async def list_pvcs(namespace: Optional[str] = None) -> list[PersistentVolumeClaim]:
    """
    List PersistentVolumeClaims (PVCs) in the Kubernetes cluster.
    If a namespace is provided, list PVCs only in that namespace.
    """
    try:
        if namespace:
            pvcs = core_v1_api.list_namespaced_persistent_volume_claim(namespace=namespace)
        else:
            pvcs = core_v1_api.list_persistent_volume_claim_for_all_namespaces()

        return [
            PersistentVolumeClaim(
                name=pvc.metadata.name,
                namespace=pvc.metadata.namespace,
                status=pvc.status.phase,
                storage=pvc.status.capacity.get("storage") if pvc.status.capacity else None,
                access_modes=pvc.spec.access_modes,
                storage_class=pvc.spec.storage_class_name,
            )
            for pvc in pvcs.items
        ]
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching PVCs: {e.reason}")

async def list_pvs(namespace: Optional[str] = None) -> list[PersistentVolume]:
    """
    List PersistentVolumes (PVs) in the Kubernetes cluster.
    If a namespace is provided, filter PVs by their claimRef namespace.
    """
    try:
        pvs = core_v1_api.list_persistent_volume()

        # Filter PVs by namespace if provided
        filtered_pvs = [
            pv for pv in pvs.items
            if not namespace or (pv.spec.claim_ref and pv.spec.claim_ref.namespace == namespace)
        ]

        return [
            PersistentVolume(
                name=pv.metadata.name,
                status=pv.status.phase,
                capacity=pv.spec.capacity.get("storage") if pv.spec.capacity else None,
                access_modes=pv.spec.access_modes,
                reclaim_policy=pv.spec.persistent_volume_reclaim_policy,
                storage_class=pv.spec.storage_class_name,
                volume_mode=pv.spec.volume_mode,
            )
            for pv in filtered_pvs
        ]
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching PVs: {e.reason}")

