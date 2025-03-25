from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from base.routers import router as base_router
from v1.routers.resources import router as v1_resources_router
from base.security.audit import AuditLogMiddlewares

app = FastAPI()
app_v1 = FastAPI(
    servers=[
        {"url": "/v1", "description": "V1 environment"},
        {
            "url": "https://api.itlusions.com/servicediscovery/v1",
            "description": "V1 environment",
        },
    ]
)

app.include_router(base_router, tags=["Health"])
app_v1.include_router(v1_discovery_router)
app.add_middleware(AuditLogMiddleware)

app.mount("/v1", app_v1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)
