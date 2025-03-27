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