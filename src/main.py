import os
from fastapi import FastAPI, Depends
from base.auth import AuthWrapper
from base.k8s_config import load_k8s_config
from base.helpers import KubernetesHelper
from base.routers import router as base_router
from base.logging import LoggerConfigurator

from v1.routers import (
    k8s as v1_k8s_resources_router,
    resources as v1_resources_router,
    s3 as v1_s3_router,
    connection as v1_connection_router,
    crd as v1_crd_router,
    testmanager as v1_test_manager_router,
    pypi as v1_pypi_router,
    acr as v1_acr_router,
)

# Initialize logging
logger = LoggerConfigurator().configure_logging()
logger.info("Logging has been configured successfully.")

# Load Kubernetes configuration
load_k8s_config()
print("Kubernetes configuration loaded successfully.")

# Initialize KubernetesHelper
k8s_helper = KubernetesHelper()

# Display runtime context
runtime_info = k8s_helper.get_runtime_info()
print("Runtime Context:")
for key, value in runtime_info.items():
    print(f"  {key}: {value}")

# Fetch dynamic configuration from environment variables
root_path = os.getenv("ROOT_PATH", "/resource-explorer")
openapi_url = os.getenv("OPENAPI_URL", f"{root_path}/openapi.json")

auth_wrapper = AuthWrapper()

# Initialize FastAPI apps
print("FastAPI applications initialized.")
app = FastAPI(root_path=root_path, openapi_url=openapi_url)
app_v1 = FastAPI(root_path=f"{root_path}/v1", openapi_url=f"{root_path}/openapi.json")

# Include routers
app.include_router(base_router, tags=["Health"])
v1_routers = [
    (v1_resources_router.router, "Simple Resources"),
    (v1_k8s_resources_router.k8s_resources_router, "K8s Resources"),
    (v1_s3_router.router, "S3"),
    (v1_connection_router.router, "Connection"),
    (v1_test_manager_router.router, "Test"),
    (v1_crd_router.router, "K8s Resources"),
    (v1_pypi_router.router, "PyPi"),
    (v1_acr_router.router, "ACR"),
]

for router, tag in v1_routers:
    app_v1.include_router(router, tags=[tag], dependencies=[Depends(auth_wrapper.validate_api_key)])
print("FastAPI routers included successfully.")

# Mount versioned app
app.mount("/", app_v1)
print("FastAPI application mounted successfully.")

# Output app_v1 settings
print("app_v1 settings:")
print(f"Title: {app_v1.title}")
print(f"Version: {app_v1.version}")
print(f"OpenAPI URL: {app_v1.openapi_url}")
print(f"Root Path: {app_v1.root_path}")
print(f"Docs URL: {app_v1.docs_url}")
print(f"Redoc URL: {app_v1.redoc_url}")

print("FastAPI application is ready to run.")



# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True, log_level="info")
