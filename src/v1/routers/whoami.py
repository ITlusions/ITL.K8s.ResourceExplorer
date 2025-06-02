from fastapi import APIRouter, Depends, Request
from base.auth import AuthWrapper

router = APIRouter(prefix="/whoami", tags=["WhoAmI"])
auth_wrapper = AuthWrapper()

@router.get("/", summary="Show decoded JWT or API key info for the current caller")
async def whoami(
    request: Request,
    auth=Depends(lambda request: auth_wrapper.validate(request, required_resource="*"))
):
    """
    Returns the decoded JWT or API key info for the authenticated user or app.
    """
    return {"auth_info": auth}