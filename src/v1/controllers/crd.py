from fastapi import HTTPException
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from base.k8s_config import load_k8s_config

# Load Kubernetes Configurations
load_k8s_config()

api_extension_client = client.ApiextensionsV1Api()
custom_objects_api = client.CustomObjectsApi()

def list_crds():
    """
    List all Custom Resource Definitions (CRDs) in the cluster.
    """
    try:
        crds = api_extension_client.list_custom_resource_definition()
        return [{"name": crd.metadata.name, "group": crd.spec.group, "version": crd.spec.versions[0].name} for crd in crds.items]
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CRDs: {str(e)}")

def get_crd_items(group: str, version: str, plural: str, namespace: str = None):
    """
    Get items from a specific CRD.

    Args:
        group (str): The API group of the CRD.
        version (str): The version of the CRD.
        plural (str): The plural name of the CRD (e.g., "customresources").
        namespace (str, optional): The namespace to query (if the CRD is namespaced).

    Returns:
        list: A list of items from the specified CRD.
    """
    try:
        if namespace:
            items = custom_objects_api.list_namespaced_custom_object(
                group=group,
                version=version,
                namespace=namespace,
                plural=plural,
            )
        else:
            items = custom_objects_api.list_cluster_custom_object(
                group=group,
                version=version,
                plural=plural,
            )
        return items
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CRD items: {str(e)}")