from fastapi import HTTPException
from typing import Optional, Callable
from pydantic import BaseModel
import os

class KubernetesHelper:
    """
    A helper class for Kubernetes-related operations.
    """

    def __init__(self):
        """
        Initialize the KubernetesHelper object.
        """
        self.namespace = self.get_namespace()

    def get_namespace(self) -> str:
        """
        Retrieve the Kubernetes namespace.

        Example:
            helper = KubernetesHelper()
            print(helper.namespace)  # Outputs the current namespace or raises an HTTPException if not found.
        """
        try:
            return os.getenv("NAMESPACE", open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read().strip())
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Namespace file not found.")
        
    

    def get_pod_name(self) -> Optional[str]:
        """
        Retrieve the name of the current pod.

        Returns:
            The pod name if available, otherwise None.
        """
        return os.getenv("POD_NAME")

    def get_service_account(self) -> Optional[str]:
        """
        Retrieve the name of the service account used by the pod.

        Returns:
            The service account name if available, otherwise None.
        """
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as token_file:
                return token_file.read().strip()
        except FileNotFoundError:
            return None

    def is_running_in_kubernetes(self) -> bool:
        """
        Check if the application is running inside a Kubernetes cluster.

        Returns:
            True if running in Kubernetes, False otherwise.
        """
        return os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/namespace")
    
    def get_kube_config(self) -> Optional[str]:
        """
        Retrieve the Kubernetes configuration file content.

        Returns:
            The content of the kubeconfig file if available, otherwise None.
        """
        kube_config_path = os.getenv("KUBECONFIG", os.path.expanduser("~/.kube/config"))
        try:
            with open(kube_config_path, "r") as kube_config_file:
                return kube_config_file.read()
        except FileNotFoundError:
            return None

    def get_node_name(self) -> Optional[str]:
        """
        Retrieve the name of the node where the pod is running.

        Returns:
            The node name if available, otherwise None.
        """
        return os.getenv("NODE_NAME")

    def get_labels(self) -> Optional[dict]:
        """
        Retrieve the labels assigned to the pod.

        Returns:
            A dictionary of labels if available, otherwise None.
        """
        labels = os.getenv("POD_LABELS")
        if labels:
            try:
                import json
                return json.loads(labels)
            except json.JSONDecodeError:
                return None
        return None

    def get_annotations(self) -> Optional[dict]:
        """
        Retrieve the annotations assigned to the pod.

        Returns:
            A dictionary of annotations if available, otherwise None.
        """
        annotations = os.getenv("POD_ANNOTATIONS")
        if annotations:
            try:
                import json
                return json.loads(annotations)
            except json.JSONDecodeError:
                return None
        return None

    def get_cluster_name(self) -> Optional[str]:
        """
        Retrieve the name of the Kubernetes cluster.

        Returns:
            The cluster name if available, otherwise None.
        """
        return os.getenv("CLUSTER_NAME")

    def get_container_id(self) -> Optional[str]:
        """
        Retrieve the container ID.

        Returns:
            The container ID if available, otherwise None.
        """
        return os.getenv("CONTAINER_ID")

    def get_environment_variables(self) -> dict:
        """
        Retrieve all environment variables available to the pod.

        Returns:
            A dictionary of environment variables.
        """
        return dict(os.environ)

    def get_runtime_info(self) -> dict:
        """
        Retrieve runtime information about the pod.

        Returns:
            A dictionary containing runtime information.
        """
        return {
            "namespace": self.get_namespace(),
            "pod_name": self.get_pod_name(),
            "node_name": self.get_node_name(),
            "container_id": self.get_container_id(),
        }

    def get_resource_limits(self) -> dict:
        """
        Retrieve resource limits (CPU and memory) for the pod.

        Returns:
            A dictionary containing resource limits.
        """
        return {
            "cpu_limit": os.getenv("CPU_LIMIT"),
            "memory_limit": os.getenv("MEMORY_LIMIT"),
        }

