import os
import uuid
import base64
import logging
import jwt
from jwt import PyJWKClient
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from kubernetes import client, config
from base.helpers import KubernetesHelper
from typing import Optional, Union

# Configure logging for this module
logger = logging.getLogger("AuthWrapper")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class AuthWrapper:
    def __init__(self, enable_validation: bool = True):
        self.app = FastAPI()
        self.API_KEY_NAME = "X-API-Key"
        self.api_key_header = APIKeyHeader(name=self.API_KEY_NAME, auto_error=False)
        self.k8s_helper = KubernetesHelper()
        self.enable_validation = enable_validation
        self.logger = logger
        self.enable_apikey = os.getenv("ENABLE_APIKEY", "true").lower() == "true"
        self.enable_oauth2 = os.getenv("ENABLE_OAUTH2", "true").lower() == "true"

        # Initialize API key
        self.API_KEY = self._initialize_api_key()

        # OAuth2 Authorization Code flow config for Keycloak
        self.oauth2_scheme = OAuth2AuthorizationCodeBearer(
            authorizationUrl=os.getenv(
                "OAUTH2_AUTH_URL",
                "https://sts.itlusions.com/realms/itlusions/protocol/openid-connect/auth"
            ),
            tokenUrl=os.getenv(
                "OAUTH2_TOKEN_URL",
                "https://sts.itlusions.com/realms/itlusions/protocol/openid-connect/token"
            ),
            scopes={"openid": "OpenID Connect scope"}
        )

        # OAuth2 Client Credentials flow config
        self.oauth2_client_credentials_scheme = OAuth2PasswordBearer(
            tokenUrl=os.getenv(
                "OAUTH2_TOKEN_URL",
                "https://sts.itlusions.com/realms/itlusions/protocol/openid-connect/token"
            ),
            scopes={"openid": "OpenID Connect scope"}
        )

        # JWKS URL for Keycloak
        self.jwks_url = os.getenv(
            "KEYCLOAK_JWKS_URL",
            "https://sts.itlusions.com/realms/itlusions/protocol/openid-connect/certs"
        )

    def _initialize_api_key(self) -> str:
        """
        Initialize the API key by retrieving it from a Kubernetes secret or environment variable,
        or generating a fallback key for local testing.
        """
        try:
            secret_name = os.getenv("API_SECRET_NAME", "re-api-key")
            namespace = self.k8s_helper.get_namespace()
            secret_key = os.getenv("API_SECRET_KEY", "api-key")

            self.logger.info(f"Using secret_name: {secret_name}, namespace: {namespace}, secret_key: [MASKED]")
            self.logger.info(f"Attempting to retrieve API key from Kubernetes secret: {secret_name}")
            api_key = self.get_api_key_from_k8s_secret(secret_name, namespace, secret_key)
            self.logger.info("Successfully retrieved API key from Kubernetes secret.")
            self.logger.info(f"API key created-on: {self.extract_api_key_data(api_key).get('timestamp') if self.extract_api_key_data(api_key) else 'N/A'}")
            
            return api_key
        except Exception as e:
            self.logger.warning(f"Failed to retrieve API key from Kubernetes secret: {e}")
            env_api_key = os.getenv("FALLBACK_API_KEY")
            if env_api_key:
                self.logger.info("Using API key from environment variable.")
                return env_api_key

            fallback_key = self._generate_fallback_key()
            self.logger.warning("Using fallback API key for local testing.")
            self.logger.debug(f"Generated fallback API key: {fallback_key}")
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
    
    def extract_api_key_data(self, api_key: str, strict: bool = False) -> Optional[dict]:
        """
        Decode and extract data from the API key if possible.

        Args:
            api_key (str): The API key to decode and extract.
            strict (bool): If True, raise exception on decode/extract failure. If False, return None.

        Returns:
            Optional[dict]: Extracted data if successful, None otherwise.

        Raises:
            Exception: If strict is True and decoding or extraction fails.
        """
        try:
            decoded = base64.b64decode(api_key).decode("utf-8")
            parts = decoded.split(":")
            if len(parts) == 4:
                releasename, timestamp, randomstring, checksum = parts
                self.logger.debug(
                    f"Extracted from API key - releasename: {releasename}, timestamp: {timestamp}, randomstring: {randomstring}, checksum: {checksum}"
                )
                return {
                    "releasename": releasename,
                    "timestamp": timestamp,
                    "randomstring": randomstring,
                    "checksum": checksum,
                }
            else:
                self.logger.warning("API key format is invalid for extraction.")
                if strict:
                    raise ValueError("API key format is invalid for extraction.")
        except Exception as e:
            self.logger.warning(f"Failed to decode or extract API key data: {e}")
            if strict:
                raise
        return None

    def get_keycloak_public_key(self, token: str):
        """
        Fetch the public key from Keycloak's JWKS endpoint and use it to verify the token.
        """
        try:
            jwk_client = PyJWKClient(self.jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            return signing_key.key
        except Exception as e:
            self.logger.error(f"Failed to fetch public key from Keycloak: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch public key from Keycloak"
            )

    async def validate(
        self,
        request: Request,
        api_key: Optional[str] = Depends(APIKeyHeader(name="X-API-Key", auto_error=False)),
        token: Optional[str] = Depends(lambda: None),
        client_token: Optional[str] = Depends(lambda: None),
        required_group: Optional[str] = None,
        required_resource: Optional[str] = None,
    ) -> Union[dict, str]:
        """
        Accepts a valid API key, a valid OAuth2 user token, or a valid OAuth2 client credentials token.
        Returns user info or API key info if valid, else raises HTTPException.
        Enforces group membership and resource access if required.
        """
        # Try API key
        if api_key and api_key == self.API_KEY:
            self.logger.info("Authenticated using API key.")
            return {"auth_type": "api_key"}

        # Try OAuth2 Authorization Code flow (user)
        token = await self.oauth2_scheme(request)
        if token:
            try:
                public_key = self.get_keycloak_public_key(token)
                decoded = jwt.decode(
                    token,
                    key=public_key,
                    algorithms=["RS256"],
                    audience=os.getenv("OAUTH2_CLIENT_ID")
                )
                groups = decoded.get("groups", [])
                resource_access = decoded.get("resource_access", {})
                if required_resource and required_resource != "*" and required_resource not in resource_access:
                    self.logger.warning(f"User does not have access to resource: {required_resource}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"User does not have access to resource '{required_resource}'"
                    )
                if required_group and required_group not in groups:
                    self.logger.warning(f"User not in required group: {required_group}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"User must be a member of group '{required_group}'"
                    )
                self.logger.info("Authenticated using OAuth2 user token.")
                return {
                    "auth_type": "oauth2_user",
                    "access_token": token,
                    "groups": groups,
                    "resource_access": resource_access
                }
            except jwt.ExpiredSignatureError:
                self.logger.warning("Token has expired.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            except jwt.InvalidTokenError as e:
                self.logger.warning(f"Invalid token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or malformed user token"
                )

        # Try OAuth2 Client Credentials flow (app)
        client_token = await self.oauth2_client_credentials_scheme(request)
        if client_token:
            try:
                public_key = self.get_keycloak_public_key(client_token)
                decoded = jwt.decode(
                    client_token,
                    key=public_key,
                    algorithms=["RS256"],
                    audience=os.getenv("OAUTH2_CLIENT_ID")
                )
                resource_access = decoded.get("resource_access", {})
                groups = []
                for client, access in resource_access.items():
                    groups.extend(access.get("roles", []))
                if required_resource and required_resource != "*" and required_resource not in resource_access:
                    self.logger.warning(f"App does not have access to resource: {required_resource}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"App does not have access to resource '{required_resource}'"
                    )
                if required_group and required_group not in groups:
                    self.logger.warning(f"App not in required group: {required_group}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"App must be a member of group '{required_group}'"
                    )
                self.logger.info("Authenticated using OAuth2 client credentials token.")
                return {
                    "auth_type": "oauth2_app",
                    "access_token": client_token,
                    "groups": groups,
                    "resource_access": resource_access
                }
            except jwt.ExpiredSignatureError:
                self.logger.warning("Client token has expired.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Client token has expired"
                )
            except jwt.InvalidTokenError as e:
                self.logger.warning(f"Invalid client token: {e}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or malformed client token"
                )

        self.logger.warning("Authentication failed: No valid API key or OAuth2 token.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authenticated (API key or OAuth2 token required)",
        )