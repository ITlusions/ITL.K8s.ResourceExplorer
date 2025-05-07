import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from kubernetes import client, config

app = FastAPI()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def get_api_key_from_k8s_secret(secret_name: str, namespace: str, key: str) -> str:
    """
    Retrieve the API key from a Kubernetes secret.
    """
    try:
        # Load Kubernetes configuration
        config.load_incluster_config()  # Use in-cluster config for Kubernetes
        clientv1 = client.CoreV1Api()
        
        # Retrieve the secret
        secret = clientv1.read_namespaced_secret(name=secret_name, namespace=namespace)
        
        # Decode the API key from the secret
        if key not in secret.data:
            raise KeyError(f"Key '{key}' not found in Kubernetes secret '{secret_name}'")
        
        # Decode the base64-encoded secret value
        return secret.data[key].encode("utf-8").decode("utf-8")
    except client.ApiException as e:
        raise RuntimeError(f"Failed to retrieve Kubernetes secret '{secret_name}': {e.reason}")
    except KeyError as e:
        raise RuntimeError(str(e))
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")

# Replace these with your Kubernetes secret details
try:
    SECRET_NAME = os.getenv("API_SECRET_NAME", "re-api-key")
    NAMESPACE = os.getenv("NAMESPACE", open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read().strip())
    SECRET_KEY = os.getenv("API_SECRET_KEY", "api-key")

    # Retrieve the API key from the Kubernetes secret
    API_KEY = get_api_key_from_k8s_secret(SECRET_NAME, NAMESPACE, SECRET_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize API key: {e}") from e

def validate_api_key(api_key: str = Depends(api_key_header)):
    """
    Validate the provided API key against the one retrieved from the Kubernetes secret.
    """
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
