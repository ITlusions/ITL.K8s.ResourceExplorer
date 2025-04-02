from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ArtifactoryTestRequest(BaseModel):
    repository_url: HttpUrl = Field(
        default="https://pypi.org/simple", 
        description="The URL of the PyPI repository (default: https://pypi.org/simple)"
    )
    username: Optional[str] = Field(None, description="Username for authentication (optional)")
    password: Optional[str] = Field(None, description="Password for authentication (optional)")
    skip_tls_verify: bool = Field(False, description="Skip TLS certificate verification (default: False)")