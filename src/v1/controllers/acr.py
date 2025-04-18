from azure.identity import ClientSecretCredential, DeviceCodeCredential
from azure.containerregistry import ContainerRegistryClient
from fastapi import HTTPException
from typing import List, Dict

def authenticate_to_acr(client_id: str, client_secret: str, tenant_id: str):
    try:
        print(f"Authenticating with Tenant ID: {tenant_id}, Client ID: {client_id}")
        credential = ClientSecretCredential(
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
        )
        # Test the credential by requesting a token
        token = credential.get_token("https://management.azure.com/.default")
        print(f"Authentication successful. Token: {token.token[:10]}...")
        return credential
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

def authenticate_to_azure(subscription_id: str):
    """
    Authenticate to Azure using Device Code flow.
    """
    try:
        print("Authenticating to Azure using Device Code...")
        credential = DeviceCodeCredential()
        print("Successfully authenticated to Azure.")
        return credential
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Azure authentication failed: {str(e)}")

def list_acr_repositories_and_images(
    registry_url: str,
    token_username: str = None,
    token_password: str = None,
    client_id: str = None,
    client_secret: str = None,
    tenant_id: str = None,
) -> dict:
    """
    Authenticates to an Azure Container Registry (ACR) using either a repository-scoped token
    or Azure Active Directory credentials, and retrieves a list of repositories and their images.

    Args:
        registry_url (str): The URL of the ACR (e.g., "myregistry.azurecr.io").
        token_username (str, optional): The username of the repository-scoped token.
        token_password (str, optional): The password of the repository-scoped token.
        client_id (str, optional): Client ID for Azure Active Directory authentication.
        client_secret (str, optional): Client secret for Azure Active Directory authentication.
        tenant_id (str, optional): Tenant ID for Azure Active Directory authentication.

    Returns:
        dict: A dictionary containing repositories and their associated image tags.
    """
    try:
        # Determine the authentication method
        if token_username and token_password:
            # Authenticate using repository-scoped token
            credential = (token_username, token_password)
        elif client_id and client_secret and tenant_id:
            # Authenticate using Azure Active Directory credentials
            credential = ClientSecretCredential(
                client_id=client_id,
                client_secret=client_secret,
                tenant_id=tenant_id,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid authentication parameters. Provide either token_username/token_password or client_id/client_secret/tenant_id.",
            )

        # Create the ACR client
        client = ContainerRegistryClient(endpoint=registry_url, credential=credential)

        # Fetch repositories
        repositories = client.list_repository_names()

        # Fetch image tags for each repository
        repo_images = {}
        for repo in repositories:
            tags = client.list_tag_properties(repository_name=repo)
            repo_images[repo] = [tag.name for tag in tags]

        return {"registry_url": registry_url, "repositories": repo_images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repositories/images: {str(e)}")

def list_acr_repositories(subscription_id: str, registry_name: str) -> Dict[str, List[str]]:
    """
    List repositories and their tags in an Azure Container Registry.
    """
    try:
        # Authenticate to Azure
        credential = authenticate_to_azure(subscription_id)

        # Initialize the Container Registry client
        registry_url = f"https://{registry_name}.azurecr.io"
        acr_client = ContainerRegistryClient(endpoint=registry_url, credential=credential)

        # Fetch repositories and their tags
        repositories = {}
        for repo_name in acr_client.list_repository_names():
            tags = [tag.name for tag in acr_client.list_tag_properties(repository_name=repo_name)]
            repositories[repo_name] = tags

        return repositories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list repositories: {str(e)}")

def copy_acr_image_with_credentials(
    source_registry_url: str,
    source_repository: str,
    source_image_tag: str,
    source_client_id: str,
    source_client_secret: str,
    source_tenant_id: str,
    destination_registry_url: str,
    destination_repository: str,
    destination_client_id: str,
    destination_client_secret: str,
    destination_tenant_id: str,
) -> dict:
    """
    Copies a Docker image from one Azure Container Registry (ACR) to another using different credentials.

    Args:
        source_registry_url (str): The URL of the source ACR (e.g., "source.azurecr.io").
        source_repository (str): The repository name in the source ACR.
        source_image_tag (str): The image tag in the source ACR.
        source_client_id (str): Client ID for the source ACR.
        source_client_secret (str): Client secret for the source ACR.
        source_tenant_id (str): Tenant ID for the source ACR.
        destination_registry_url (str): The URL of the destination ACR (e.g., "destination.azurecr.io").
        destination_repository (str): The repository name in the destination ACR.
        destination_client_id (str): Client ID for the destination ACR.
        destination_client_secret (str): Client secret for the destination ACR.
        destination_tenant_id (str): Tenant ID for the destination ACR.

    Returns:
        dict: A dictionary containing the source and destination details.
    """
    try:
        # Authenticate to the source registry
        source_credential = authenticate_to_acr(source_client_id, source_client_secret, source_tenant_id)
        source_client = ContainerRegistryClient(
            endpoint=source_registry_url, credential=source_credential
        )

        # Authenticate to the destination registry
        destination_credential = authenticate_to_acr(destination_client_id, destination_client_secret, destination_tenant_id)
        destination_client = ContainerRegistryClient(
            endpoint=destination_registry_url, credential=destination_credential
        )

        # Get the manifest of the source image
        manifest = source_client.get_manifest_properties(
            repository_name=source_repository, tag=source_image_tag
        )

        # Copy the image to the destination registry
        destination_client.import_image(
            source=source_registry_url,
            source_repository=source_repository,
            source_tag=source_image_tag,
            repository_name=destination_repository,
            tag=source_image_tag,
        )

        return {
            "source": {
                "registry_url": source_registry_url,
                "repository": source_repository,
                "image_tag": source_image_tag,
            },
            "destination": {
                "registry_url": destination_registry_url,
                "repository": destination_repository,
                "image_tag": source_image_tag,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to copy image: {str(e)}")

def copy_acr_image(
    subscription_id: str,
    source_registry: str,
    source_repository: str,
    source_image_tag: str,
    destination_registry: str,
    destination_repository: str,
) -> Dict:
    """
    Copy an image from one Azure Container Registry to another.
    """
    try:
        # Authenticate to Azure
        credential = authenticate_to_azure(subscription_id)

        # Initialize the Container Registry clients
        source_registry_url = f"https://{source_registry}.azurecr.io"
        destination_registry_url = f"https://{destination_registry}.azurecr.io"
        source_client = ContainerRegistryClient(endpoint=source_registry_url, credential=credential)
        destination_client = ContainerRegistryClient(endpoint=destination_registry_url, credential=credential)

        # Pull the image from the source registry
        manifest = source_client.get_manifest_properties(repository_name=source_repository, tag=source_image_tag)

        # Import the image to the destination registry
        destination_client.import_image(
            source=source_registry_url,
            source_repository=source_repository,
            source_tag=source_image_tag,
            repository_name=destination_repository,
            tag=source_image_tag,
        )

        return {
            "source": {
                "registry_url": source_registry_url,
                "repository": source_repository,
                "image_tag": source_image_tag,
            },
            "destination": {
                "registry_url": destination_registry_url,
                "repository": destination_repository,
                "image_tag": source_image_tag,
            },
            "status": "success",
            "message": "Image copied successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to copy image: {str(e)}")