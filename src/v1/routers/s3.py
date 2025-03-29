from fastapi import APIRouter, Depends
from pydantic import BaseModel
from v1.models.models import S3Account, S3AccountRequest
from v1.models.s3 import (
    S3UserCreateRequest,
    S3UserUpdateRequest,
    S3UserDeleteRequest,
    S3UserResponse,
)
from v1.controllers.s3 import (
    test_s3_account as controller_test_s3_account,
    create_user,
    get_user,
    update_user,
    delete_user,
)

router = APIRouter(prefix="/s3", tags=["S3"])

def get_s3_account(request: S3AccountRequest = Depends()):
    """
    Dependency to extract S3 account details from the request.
    """
    return {
        "access_key": request.access_key,
        "secret_key": request.secret_key,
        "endpoint_url": request.endpoint_url,
        "secure_flag": request.secure_flag,
        "cert_check": request.cert_check,
    }

@router.post("/test")
def test_s3_account_endpoint(
    s3_account: dict = Depends(get_s3_account)
):
    """
    Endpoint to test S3 account credentials.
    """
    return controller_test_s3_account(**s3_account)

@router.post("/users/", response_model=S3UserResponse)
def create_s3_user(
    request: S3UserCreateRequest,
    s3_account: dict = Depends(get_s3_account)
):
    """
    Create a new S3 user.
    """
    return create_user(
        username=request.username,
        policy_arn=request.policy_arn,
        **s3_account
    )

@router.get("/users/{username}", response_model=S3UserResponse)
def get_s3_user(
    username: str,
    s3_account: dict = Depends(get_s3_account)
):
    """
    Get details of an S3 user.
    """
    return get_user(username=username, **s3_account)

@router.put("/users/", response_model=dict)
def update_s3_user(
    request: S3UserUpdateRequest,
    s3_account: dict = Depends(get_s3_account)
):
    """
    Update an S3 user (e.g., rename the user).
    """
    return update_user(
        username=request.username,
        new_username=request.new_username,
        **s3_account
    )

@router.delete("/users/", response_model=dict)
def delete_s3_user(
    request: S3UserDeleteRequest,
    s3_account: dict = Depends(get_s3_account)
):
    """
    Delete an S3 user.
    """
    return delete_user(username=request.username, **s3_account)