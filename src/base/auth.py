import os
import uuid
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

class AuthWrapper:
    def __init__(self):
        self.app = FastAPI()
        self.API_KEY_NAME = "X-API-Key"
        self.api_key_header = APIKeyHeader(name=self.API_KEY_NAME, auto_error=True)
        self.API_KEY = self._initialize_api_key()

    def _initialize_api_key(self) -> str:
        """
        Initialize the API key by retrieving it from a Kubernetes secret or generating a fallback key.
        """
        try:
            secret_name = os.getenv("API_SECRET_NAME", "re-api-key")
            namespace = os.getenv("NAMESPACE", open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read().strip())
            secret_key = os.getenv("API_SECRET_KEY", "api-key")
            
            print(f"Using secret_name: {secret_name}, namespace: {namespace}, secret_key: {secret_key}")
            
            return self.get_api_key_from_k8s_secret(secret_name, namespace, secret_key)
        except Exception:
            fallback_key = str(uuid.uuid4())
            print(f"No secrets or environment variables found.")
            print(f"Use a predefined API-Key only use this locally for testing purpose. Generated API Key: {fallback_key}")
            return fallback_key

    def get_api_key_from_k8s_secret(self, secret_name: str, namespace: str, key: str) -> str:
        """
        Retrieve the API key from a Kubernetes secret.
        """
        try:
            config.load_incluster_config()
            clientv1 = client.CoreV1Api()
            secret = clientv1.read_namespaced_secret(name=secret_name, namespace=namespace)
            
            if key not in secret.data:
                raise KeyError(f"Key '{key}' not found in Kubernetes secret '{secret_name}'")
            return secret.data[key].encode("utf-8").decode("utf-8")
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