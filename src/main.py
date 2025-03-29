import os
from fastapi import FastAPI
from base.routers import router as base_router
from base.k8s_config import load_k8s_config
from v1.routers import (
    resources as v1_resources_router,
    describe as v1_k8s_resources_router,
    s3 as v1_s3_router,
    connection as v1_connection_router,
    crd as v1_crd_router,
    testmanager as v1_test_manager_router,
)

# Load Kubernetes configuration
load_k8s_config()

# Fetch dynamic configuration from environment variables
root_path = os.getenv("ROOT_PATH", "/resource-explorer")
openapi_url = os.getenv("OPENAPI_URL", f"{root_path}/openapi.json")

# Initialize FastAPI apps
app = FastAPI(root_path=root_path, openapi_url=openapi_url)
app_v1 = FastAPI(openapi_url=f"{root_path}/v1/openapi.json")

# Include routers
app.include_router(base_router, tags=["Health"])
v1_routers = [
    (v1_resources_router.router, "Simple Resources"),
    (v1_k8s_resources_router.k8s_resources_router, "K8s Resources"),
    (v1_s3_router.router, "S3"),
    (v1_connection_router.router, "Connection"),
    (v1_test_manager_router.router, "Test"),
    (v1_crd_router.router, "K8s Resources"),
]

for router, tag in v1_routers:
    app_v1.include_router(router, tags=[tag])

# Mount versioned app
app.mount("/v1", app_v1)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)