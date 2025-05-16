from fastapi import HTTPException
from kubernetes.client.exceptions import ApiException
from kubernetes import client, config
from typing import List, Dict, Optional
from base.k8s_config import load_k8s_config

# Load Kubernetes Configurations
load_k8s_config()
core_v1_api = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()

def get_all_namespaces() -> List[str]:
    """
    List all namespaces in the Kubernetes cluster.
    
    Returns:
        List[str]: A list of namespace names.
    """
    try:
        namespaces = core_v1_api.list_namespace()
        namespace_names = [ns.metadata.name for ns in namespaces.items]
        return namespace_names
    except client.exceptions.ApiException as e:
        print(f"Error listing namespaces: {e}")
        return []

def get_all_secrets() -> List[Dict[str, str]]:
    """
    List all secrets in the Kubernetes cluster.
    
    Returns:
        List[Dict[str, str]]: A list of secret names and their corresponding namespaces.
    """
    try:
        secrets = core_v1_api.list_secret_for_all_namespaces()
        secret_names = [{"name": secret.metadata.name, "namespace": secret.metadata.namespace} for secret in secrets.items]
        return secret_names
    except client.exceptions.ApiException as e:
        print(f"Error listing secrets: {e}")
        return []

def list_resources_grouped_by_namespace():
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
        raise HTTPException(status_code=500, detail=f"Error fetching resources: {str(e)}")

def delete_deployment(namespace: str, deployment_name: str):
    try:
        # Load Kubernetes configuration
        config.load_kube_config()

        # Create an API client for deployments
        apps_v1 = client.AppsV1Api()

        # Delete the deployment
        response = apps_v1.delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=client.V1DeleteOptions()
        )
        return {"message": f"Deployment '{deployment_name}' deleted successfully", "details": response.status}
    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Failed to delete deployment: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def delete_resource(namespace: str, resource_name: str, resource_type: str, force: bool = False):
    """
    Delete a Kubernetes resource (Deployment, StatefulSet, ReplicaSet, Pod, PersistentVolume, PersistentVolumeClaim, Namespace).

    Args:
        namespace (str): The namespace of the resource (not required for PersistentVolumes or Namespaces).
        resource_name (str): The name of the resource to delete.
        resource_type (str): The type of the resource (deployment, statefulset, replicaset, pod, pv, pvc, namespace).
        force (bool): Whether to force delete the resource.

    Returns:
        dict: A success message and details of the deletion.
    """
    try:
        delete_options = client.V1DeleteOptions(
            grace_period_seconds=0 if force else None,
            propagation_policy="Foreground" if force else "Background"
        )

        resource_deletion_map = {
            "deployment": apps_v1_api.delete_namespaced_deployment,
            "statefulset": apps_v1_api.delete_namespaced_stateful_set,
            "replicaset": apps_v1_api.delete_namespaced_replica_set,
            "pod": core_v1_api.delete_namespaced_pod,
            "pvc": core_v1_api.delete_namespaced_persistent_volume_claim,
            "pv": core_v1_api.delete_persistent_volume,
            "namespace": core_v1_api.delete_namespace,
        }

        if resource_type.lower() in resource_deletion_map:
            delete_func = resource_deletion_map[resource_type.lower()]
            response = delete_func(
                name=resource_name,
                namespace=namespace if resource_type.lower() not in ["pv", "namespace"] else None,
                body=delete_options
            )
            return {"message": f"{resource_type.capitalize()} '{resource_name}' deleted successfully", "details": response.to_dict() if hasattr(response, 'to_dict') else str(response)}
        else:
            print(f"Unsupported resource type: {resource_type}")
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")

    except client.exceptions.ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()} '{resource_name}' not found")
        raise HTTPException(status_code=e.status, detail=f"Failed to delete {resource_type}: {e.reason}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while deleting {resource_type} '{resource_name}': {str(e)}"
        )