from fastapi import APIRouter, Depends
from base.auth import AuthWrapper

router = APIRouter(prefix="/auth")
auth_wrapper = AuthWrapper()

@router.get(
    "/whoami",
    summary="Show decoded JWT, API key, or OAuth2 scheme info for the current caller",
    dependencies=[Depends(auth_wrapper.oauth2_scheme)]
)
async def whoami(
    auth=Depends(lambda request: auth_wrapper.validate(request, required_resource="*"))
):
    """
    Returns the decoded JWT, API key, or OAuth2 scheme info for the authenticated user or app.
    """
    return {"auth_info": auth}