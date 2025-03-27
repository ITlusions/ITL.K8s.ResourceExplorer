import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from base.routers import router as base_router
from base.k8s_config import load_k8s_config
from v1.routers.resources import router as v1_resources_router
from v1.routers.describe import k8s_resources_router as v1_k8s_resources_router 
from v1.routers.s3 import router as v1_s3_router
from v1.routers.connection import router as v1_connection_router
from v1.routers.crd import router as v1_crd_router

load_k8s_config()

# Fetch dynamic configuration from environment variables
root_path = os.environ.get("ROOT_PATH") if "ROOT_PATH" in os.environ else "/resource-explorer"
openapi_url = os.environ.get("OPENAPI_URL") if "OPENAPI_URL" in os.environ else f"{root_path}/openapi.json"

app = FastAPI(
    root_path=root_path,  # Prefix for the entire application
    openapi_url=openapi_url,  # Custom OpenAPI schema URL
)
app_v1 = FastAPI(
    openapi_url=f"{root_path}/v1/openapi.json",
)

app.include_router(base_router, tags=["Health"])
app_v1.include_router(v1_resources_router, tags=["Simple Resources"])
app_v1.include_router(v1_k8s_resources_router , tags=["K8s Resources"])
app_v1.include_router(v1_s3_router, tags=["S3"])
app_v1.include_router(v1_connection_router, tags=["Connection"])
app_v1.include_router(v1_crd_router, tags=["CRDs"])

app.mount("/v1", app_v1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)