from fastapi import APIRouter, HTTPException
from v1.models.pypi import ArtifactoryTestRequest
from v1.controllers.pypi import test_artifactory_repository

router = APIRouter()

@router.post("/pypi/test")
async def test_artifactory(request: ArtifactoryTestRequest):
    """
    Test the connectivity to an PyPI repository.
    """
    result = test_artifactory_repository(
        repository_url=request.repository_url,
        username=request.username,
        password=request.password,
        skip_tls_verify=request.skip_tls_verify
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result