import os
import uuid
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from typing import Optional

API_KEY_NAME = "X-API-Key"
DEFAULT_SECRET_NAME = "re-api-key"
DEFAULT_SECRET_KEY = "api-key"

class CustomAPIKeyHeader(APIKeyHeader):
    """
    Custom APIKeyHeader class to allow more advanced validation or customization.
    """
    def __init__(self, name: str, auto_error: bool = True):
        super().__init__(name=name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str:
        api_key = await super().__call__(request)
        if not api_key:
            raise HTTPException(status_code=400, detail="API Key is missing")
        if len(api_key) < 10:
            raise HTTPException(status_code=400, detail="API Key is too short")
        return api_key

api_key_header = CustomAPIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key_from_k8s_secret(secret_name: str, namespace: str, key: str) -> str:
    """
    Retrieve the API key from a Kubernetes secret.
    """
    try:
        # Load Kubernetes configuration
        try:
            config.load_incluster_config()  # Use in-cluster config for Kubernetes
        except config.ConfigException:
            config.load_kube_config()  # Fallback for local testing

        clientv1 = client.CoreV1Api()
        
        # Retrieve the secret
        secret = clientv1.read_namespaced_secret(name=secret_name, namespace=namespace)
        
        # Decode the API key from the secret
        if key not in secret.data:
            raise KeyError(f"Key '{key}' not found in Kubernetes secret '{secret_name}'")
        
        # Decode the base64-encoded secret value
        
        return secret.data[key].encode("utf-8").decode("utf-8")
    except ApiException as e:
        raise RuntimeError(f"Failed to retrieve Kubernetes secret '{secret_name}': {e.reason}")
    except KeyError as e:
        raise RuntimeError(str(e))
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

def load_api_key() -> str:
    """
    Load the API key from Kubernetes secrets or generate a random one for local testing.
    """
    try:
        secret_name = os.getenv("API_SECRET_NAME", DEFAULT_SECRET_NAME)
        namespace = os.getenv("NAMESPACE", open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read().strip())
        secret_key = os.getenv("API_SECRET_KEY", DEFAULT_SECRET_KEY)

        # Print the secret name, key, and namespace being used
        print(f"Loading API key from secret '{secret_name}' in namespace '{namespace}' with key '{secret_key}'")

        # Retrieve the API key from the Kubernetes secret
        return get_api_key_from_k8s_secret(secret_name, namespace, secret_key)
    except Exception as e:
        # Log the error and generate a random API key for local testing
        print(f"Error loading API key: {e}")
        print("Using a randomly generated API key for local testing purposes.")
        return str(uuid.uuid4())

API_KEY = load_api_key()

def validate_api_key(api_key: str = Depends(api_key_header)):
    """
    Validate the provided API key against the one retrieved from the Kubernetes secret.
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
