from fastapi import APIRouter, Depends, Request
from base.auth import AuthWrapper

router = APIRouter(prefix="/auth")
auth_wrapper = AuthWrapper()

@router.get(
    "/whoami", 
    summary="Show decoded JWT or API key info for the current caller",
    dependencies=[Depends(auth_wrapper.oauth2_scheme)]
)
async def whoami(
    request: Request,
    auth=Depends(lambda request: auth_wrapper.validate(request, required_resource="*"))
):
    """
    Returns the decoded JWT or API key info for the authenticated user or app.
    """
    return {"auth_info": auth}