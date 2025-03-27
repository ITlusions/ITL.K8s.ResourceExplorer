from fastapi import HTTPException
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from base.k8s_config import load_k8s_config

# Load Kubernetes Configurations
load_k8s_config()

core_v1_api = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()

async def describe_resource(namespace: str, resource_type: str, resource_name: str):
    try:
        if resource_type == "pod":
            resource = await core_v1_api.read_namespaced_pod(name=resource_name, namespace=namespace, async_req=True)
        elif resource_type == "service":
            resource = await core_v1_api.read_namespaced_service(name=resource_name, namespace=namespace, async_req=True)
        elif resource_type == "deployment":
            resource = await apps_v1_api.read_namespaced_deployment(name=resource_name, namespace=namespace, async_req=True)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")

        return {
            "metadata": resource.metadata.to_dict(),
            "spec": resource.spec.to_dict(),
            "status": resource.status.to_dict(),
        }
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resource: {str(e)}")
    


async def list_resources_grouped_by_namespace():
    """
    Fetch all resources (pods, services, deployments) grouped by namespace.
    """
    try:
        namespaces = (await core_v1_api.list_namespace(async_req=True)).items
        result = {}

        for ns in namespaces:
            namespace_name = ns.metadata.name

            # Fetch resources in the namespace
            pods = (await core_v1_api.list_namespaced_pod(namespace=namespace_name, async_req=True)).items
            services = (await core_v1_api.list_namespaced_service(namespace=namespace_name, async_req=True)).items
            deployments = (await apps_v1_api.list_namespaced_deployment(namespace=namespace_name, async_req=True)).items

            # Group resources by namespace
            result[namespace_name] = {
                "pods": [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods],
                "services": [{"name": svc.metadata.name, "type": svc.spec.type} for svc in services],
                "deployments": [{"name": dep.metadata.name, "replicas": dep.status.replicas} for dep in deployments],
            }

        return result

    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resources: {str(e)}")