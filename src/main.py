from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from base.routers import router as base_router
from base.k8s_config import load_k8s_config
from v1.routers.resources import router as v1_resources_router


load_k8s_config()

app = FastAPI()
app_v1 = FastAPI()

app.include_router(base_router, tags=["Health"])
app_v1.include_router(v1_resources_router)

app.mount("/v1", app_v1)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8000, reload=True)
