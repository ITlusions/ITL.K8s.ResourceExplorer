import os
import uuid
import base64
from base.helpers import KubernetesHelper
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from kubernetes import client, config

"""
# Example usage
auth_wrapper = AuthWrapper()
app = auth_wrapper.app

@app.get("/secure-endpoint")
def secure_endpoint(api_key: str = Depends(auth_wrapper.validate_api_key)):
    return {"message": "You have access to this secure endpoint!"}
"""


k8s_helper = KubernetesHelper()

class AuthWrapper:
    def __init__(self):
        self.app = FastAPI()
        self.API_KEY_NAME = "X-API-Key"
        self.api_key_header = APIKeyHeader(name=self.API_KEY_NAME, auto_error=True)
        self.API_KEY = self._initialize_api_key()
        self.decoded_api_key = None
        self.encoded_api_key = None

    def _initialize_api_key(self) -> str:
        """
        Initialize the API key by retrieving it from a Kubernetes secret or generating a fallback key.
        """
        try:
            secret_name = os.getenv("API_SECRET_NAME", "re-api-key")
            namespace = k8s_helper.get_namespace()
            secret_key = os.getenv("API_SECRET_KEY", "api-key")
            
            print(f"Using secret_name: {secret_name}, namespace: {namespace}, secret_key: {secret_key}")
            
            self.API_KEY = self.get_api_key_from_k8s_secret(secret_name, namespace, secret_key)
            
            return self.API_KEY
        except Exception:
            fallback_key = f"resource-explorer:fallback_key:{int(uuid.uuid1().time)}:{uuid.uuid4().hex}"
            fallback_key = base64.b64encode(fallback_key.encode("utf-8")).decode("utf-8")
            print(f"No secrets or environment variables found.")
            print(f"Use a predefined API-Key only use this locally for testing purpose. Generated API Key: {fallback_key}")
            return fallback_key

    def get_api_key_from_k8s_secret(self, secret_name: str, namespace: str, key: str) -> str:
        """
        Retrieve the API key from a Kubernetes secret and decode it from base64.

        Args:
            secret_name (str): The name of the Kubernetes secret.
            namespace (str): The namespace where the secret is located.
            key (str): The key in the secret containing the API key.

        Returns:
            str: The decoded API key.

        Raises:
            RuntimeError: If the secret or key is not found, or if decoding fails.
        """
        try:
            config.load_incluster_config()
            clientv1 = client.CoreV1Api()
            secret = clientv1.read_namespaced_secret(name=secret_name, namespace=namespace)
            
            if key not in secret.data:
                raise KeyError(f"Key '{key}' not found in Kubernetes secret '{secret_name}'")
            
            self.encoded_api_key = secret.data[key]
            self.decoded_api_key = base64.b64decode(self.encoded_api_key).decode("utf-8")

            print(f"Encoded API Key: {self.encoded_api_key}")
            print(f"Decoded API Key: {self.decoded_api_key}")

            return self.decoded_api_key
        except client.ApiException as e:
            raise RuntimeError(f"Failed to retrieve Kubernetes secret '{secret_name}': {e.reason}")
        except KeyError as e:
            raise RuntimeError(str(e))
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")

    def validate_api_key(self, api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
        """
        Validate the provided API key against the one retrieved from the Kubernetes secret.
        """
        if api_key != self.API_KEY:
            raise HTTPException(status_code=403, detail="Invalid API Key")
        return api_key