import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from base.routers import router as base_router
from base.k8s_config import load_k8s_config
from v1.routers.resources import router as v1_resources_router
from v1.routers.describe import router as v1_describe_router
from v1.routers.s3 import router as v1_s3_router
from v1.routers.connection import router as v1_connection_router

load_k8s_config()

ROOT_PATH = os.getenv("ROOT_PATH", "/resource-explorer")  # Default to "/resource-explorer"
OPENAPI_URL = os.getenv("OPENAPI_URL", f"{ROOT_PATH}/openapi.json")
DOCS_URL = os.getenv("DOCS_URL", f"{ROOT_PATH}/docs")
REDOC_URL = os.getenv("REDOC_URL", f"{ROOT_PATH}/redoc")

app = FastAPI(
    root_path=ROOT_PATH,  # Prefix for the entire application
    openapi_url=OPENAPI_URL,  # Custom OpenAPI schema URL
    docs_url=DOCS_URL,  # Custom Swagger UI URL
    redoc_url=REDOC_URL,  # Custom ReDoc URL
)

# Fetch dynamic configuration for versioned API
V1_OPENAPI_URL = os.getenv("V1_OPENAPI_URL", f"{ROOT_PATH}/v1/openapi.json")
V1_DOCS_URL = os.getenv("V1_DOCS_URL", f"{ROOT_PATH}/v1/docs")
V1_REDOC_URL = os.getenv("V1_REDOC_URL", f"{ROOT_PATH}/v1/redoc")

# Initialize the versioned FastAPI application
app_v1 = FastAPI(
    openapi_url=V1_OPENAPI_URL,  # Custom OpenAPI schema URL for v1
    docs_url=V1_DOCS_URL,  # Custom Swagger UI URL for v1
    redoc_url=V1_REDOC_URL,  # Custom ReDoc URL for v1
)

app.include_router(base_router, tags=["Health"])
app_v1.include_router(v1_resources_router, tags=["Simple Resources"])
app_v1.include_router(v1_describe_router, tags=["Describe Resources"])
app_v1.include_router(v1_s3_router, tags=["S3"])
app_v1.include_router(v1_connection_router, tags=["Connection"])

print(f"ROOT_PATH: {ROOT_PATH}")
print(f"OPENAPI_URL: {OPENAPI_URL}")
print(f"DOCS_URL: {DOCS_URL}")
print(f"REDOC_URL: {REDOC_URL}")
print(f"V1_OPENAPI_URL: {V1_OPENAPI_URL}")
print(f"V1_DOCS_URL: {V1_DOCS_URL}")
print(f"V1_REDOC_URL: {V1_REDOC_URL}")  


app.mount("/v1", app_v1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)