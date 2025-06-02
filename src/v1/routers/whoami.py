from fastapi import APIRouter, Depends, Request
from base.auth import AuthWrapper

router = APIRouter(prefix="/auth")
auth_wrapper = AuthWrapper()

async def get_auth_info(request: Request):
    return await auth_wrapper.validate(request, required_resource="*")

@router.get(
    "/whoami", 
    summary="Show decoded JWT, API key, or OAuth2 scheme info for the current caller",
    dependencies=[Depends(auth_wrapper.oauth2_scheme)]
)
async def whoami(
    auth=Depends(get_auth_info)
):
    """
    Returns the decoded JWT, API key, or OAuth2 scheme info for the authenticated user or app.
    """
    return {"auth_info": auth}