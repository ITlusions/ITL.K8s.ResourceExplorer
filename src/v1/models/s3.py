from pydantic import BaseModel

class S3UserCreateRequest(BaseModel):
    username: str
    policy_arn: str = None  # Optional: Attach a policy to the user

class S3UserUpdateRequest(BaseModel):
    username: str
    new_username: str

class S3UserDeleteRequest(BaseModel):
    username: str

class S3UserResponse(BaseModel):
    username: str
    user_id: str
    arn: str
    created_at: str