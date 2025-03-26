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

# Fetch dynamic configuration from environment variables
root_path = os.getenv("ROOT_PATH", "/resource-explorer")  # Default to "/resource-explorer"
openapi_url = os.getenv("OPENAPI_URL", f"{root_path}/openapi.json")
docs_url = os.getenv("DOCS_URL", f"{root_path}/docs")
redoc_url = os.getenv("REDOC_URL", f"{root_path}/redoc")

# Initialize the main FastAPI application
app = FastAPI(
    root_path=root_path,  # Prefix for the entire application
    openapi_url=openapi_url,  # Custom OpenAPI schema URL
    docs_url=docs_url,  # Custom Swagger UI URL
    redoc_url=redoc_url,  # Custom ReDoc URL
)

# Fetch dynamic configuration for versioned API
v1_openapi_url = os.getenv("V1_OPENAPI_URL", f"{root_path}/v1/openapi.json")
v1_docs_url = os.getenv("V1_DOCS_URL", f"{root_path}/v1/docs")
v1_redoc_url = os.getenv("V1_REDOC_URL", f"{root_path}/v1/redoc")

# Initialize the versioned FastAPI application
app_v1 = FastAPI(
    openapi_url=v1_openapi_url,  # Custom OpenAPI schema URL for v1
    docs_url=v1_docs_url,  # Custom Swagger UI URL for v1
    redoc_url=v1_redoc_url,  # Custom ReDoc URL for v1
)

# Include routers
app.include_router(base_router, tags=["Health"])
app_v1.include_router(v1_resources_router, tags=["Simple Resources"])
app_v1.include_router(v1_describe_router, tags=["Describe Resources"])
app_v1.include_router(v1_s3_router, tags=["S3"])
app_v1.include_router(v1_connection_router, tags=["Connection"])

# Print dynamic configuration for debugging
print(f"root_path: {root_path}")
print(f"openapi_url: {openapi_url}")
print(f"docs_url: {docs_url}")
print(f"redoc_url: {redoc_url}")
print(f"v1_openapi_url: {v1_openapi_url}")
print(f"v1_docs_url: {v1_docs_url}")
print(f"v1_redoc_url: {v1_redoc_url}")


app.mount("/v1", app_v1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)