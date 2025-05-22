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