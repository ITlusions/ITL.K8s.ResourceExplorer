from kubernetes import client, config
from typing import List, Dict, Optional
#from v1.models.registerservices.models import ServiceOnboarding
from base.k8s_config import load_k8s_config

# Load Kubernetes Configurations
v1_services, v1_ingresses = load_k8s_config()
core_v1_api = client.CoreV1Api()

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
