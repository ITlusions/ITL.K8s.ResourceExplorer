import os
import uuid
import base64
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from kubernetes import client, config
from base.helpers import KubernetesHelper
import logging
from typing import Optional

class AuthWrapper:
    def __init__(self, enable_validation: bool = True):
        """
        Initialize the AuthWrapper.

        Args:
            k8s_helper: An instance of KubernetesHelper (optional, for dependency injection).
            enable_validation: Whether to enable API key validation (useful for local development).
        """
        self.app = FastAPI()
        self.API_KEY_NAME = "X-API-Key"
        self.api_key_header = APIKeyHeader(name=self.API_KEY_NAME, auto_error=True)
        self.k8s_helper = KubernetesHelper()
        self.enable_validation = enable_validation
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Initialize API key
        self.API_KEY = self._initialize_api_key()

    def _initialize_api_key(self) -> str:
        """
        Initialize the API key by retrieving it from a Kubernetes secret or environment variable,
        or generating a fallback key for local testing.
        """
        try:
            secret_name = os.getenv("API_SECRET_NAME", "re-api-key")
            namespace = self.k8s_helper.get_namespace()
            secret_key = os.getenv("API_SECRET_KEY", "api-key")
            
            self.logger.info(f"Using secret_name: {secret_name}, namespace: {namespace}, secret_key: {secret_key}")
            self.logger.info(f"Attempting to retrieve API key from Kubernetes secret: {secret_name}")
            api_key = self.get_api_key_from_k8s_secret(secret_name, namespace, secret_key)
            self.logger.info("Successfully retrieved API key from Kubernetes secret.")
            return api_key
        except Exception as e:
            self.logger.warning(f"Failed to retrieve API key from Kubernetes secret: {e}")
            env_api_key = os.getenv("FALLBACK_API_KEY")
            if env_api_key:
                self.logger.info("Using API key from environment variable.")
                return env_api_key

            fallback_key = self._generate_fallback_key()
            self.logger.warning("Using fallback API key for local testing.")
            self.logger.warning(f"Generated fallback API key: {fallback_key}")
            self.logger.warning("This fallback API key is for local testing only and should not be used in production.")
            return fallback_key

    def _generate_fallback_key(self) -> str:
        """
        Generate a fallback API key for local testing.
        """
        fallback_key = f"resource-explorer:fallback_key:{int(uuid.uuid1().time)}:{uuid.uuid4().hex}"
        return base64.b64encode(fallback_key.encode("utf-8")).decode("utf-8")

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

            encoded_api_key = secret.data[key]
            decoded_api_key = base64.b64decode(encoded_api_key).decode("utf-8")

            self.logger.debug(f"Encoded API Key: {encoded_api_key}")
            self.logger.debug(f"Decoded API Key: {decoded_api_key}")

            return decoded_api_key
        except client.ApiException as e:
            raise RuntimeError(f"Failed to retrieve Kubernetes secret '{secret_name}': {e.reason}")
        except KeyError as e:
            raise RuntimeError(str(e))
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}")

    def validate_api_key(self, api_key: str = Depends(APIKeyHeader(name="X-API-Key"))):
        """
        Validate the provided API key against the one retrieved from the Kubernetes secret.

        Args:
            api_key: The API key provided in the request header.

        Returns:
            str: The validated API key.

        Raises:
            HTTPException: If the API key is invalid.
        """
        if not self.enable_validation:
            self.logger.info("API key validation is disabled.")
            return api_key

        if api_key != self.API_KEY:
            self.logger.warning("Invalid API key provided.")
            raise HTTPException(status_code=403, detail="Invalid API Key")

        self.logger.info("API key validated successfully.")
        return api_key