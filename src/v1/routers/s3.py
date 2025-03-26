from fastapi import APIRouter, Depends
from pydantic import BaseModel
from v1.models.models import S3Account, S3AccountRequest
from v1.controllers.s3 import (
    test_s3_account as controller_test_s3_account
)

router = APIRouter(prefix="/s3", tags=["S3"])

@router.post("/test-s3-account")
def test_s3_account_endpoint(request: S3AccountRequest):
    """
    Endpoint to test S3 account credentials.
    """
    return controller_test_s3_account(
        access_key=request.access_key,
        secret_key=request.secret_key,
        endpoint_url=request.endpoint_url,
        secure_flag=request.secure_flag,
        cert_check=request.cert_check,
    )