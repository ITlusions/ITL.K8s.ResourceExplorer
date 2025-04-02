import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Optional

def test_artifactory_repository(
    repository_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    skip_tls_verify: bool = False
) -> Dict:
    """
    Test the connectivity to an Artifactory PyPI repository.
    
    :param repository_url: The URL of the Artifactory PyPI repository.
    :param username: Optional username for authentication.
    :param password: Optional password for authentication.
    :param skip_tls_verify: Whether to skip TLS certificate verification.
    :return: A dictionary with the test result.
    """
    try:
        # Add trailing slash if not present
        if not repository_url.endswith("/"):
            repository_url += "/"

        # Test the repository URL
        response = requests.get(
            repository_url,
            auth=HTTPBasicAuth(username, password) if username and password else None,
            verify=not skip_tls_verify  # Control TLS verification
        )

        # Check the response status
        if response.status_code == 200:
            return {"status": "success", "message": "Repository is accessible"}
        elif response.status_code == 401:
            return {"status": "error", "message": "Authentication failed"}
        elif response.status_code == 403:
            return {"status": "error", "message": "Access forbidden"}
        else:
            return {"status": "error", "message": f"Unexpected response: {response.status_code}"}
    except requests.exceptions.SSLError as e:
        return {"status": "error", "message": f"SSL error: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Connection error: {str(e)}"}