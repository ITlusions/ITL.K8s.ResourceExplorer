import requests
from typing import Dict, Optional

def test_artifactory_repository_with_oauth(
    repository_url: str,
    oauth2_token: Optional[str] = None,
    skip_tls_verify: bool = False
) -> Dict:
    headers = {}
    if oauth2_token:
        headers["Authorization"] = f"Bearer {oauth2_token}"

    try:
        response = requests.get(
            repository_url,
            headers=headers,
            verify=not skip_tls_verify
        )
        if response.status_code == 200:
            return {"status": "success", "message": "Repository is accessible"}
        elif response.status_code == 401:
            return {"status": "error", "message": "Authentication failed"}
        else:
            return {"status": "error", "message": f"Unexpected response: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Connection error: {str(e)}"}