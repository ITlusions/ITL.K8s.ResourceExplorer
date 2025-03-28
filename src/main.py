import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resource Explorer</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: #121212;
                color: #ffffff;
                font-family: Arial, sans-serif;
                overflow: hidden;
            }}
            h1 {{
                text-align: center;
                margin-top: 20vh;
                font-size: 3rem;
                color: #ffffff;
            }}
            p {{
                text-align: center;
                font-size: 1.2rem;
                margin-top: 1rem;
            }}
            a {{
                color: #00bcd4;
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .cursor {{
                position: absolute;
                width: 50px;
                height: 50px;
                background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, rgba(255,255,255,0) 80%);
                border-radius: 50%;
                pointer-events: none;
                mix-blend-mode: lighten;
                animation: pulse 1.5s infinite;
            }}
            @keyframes pulse {{
                0% {{
                    transform: scale(1);
                    opacity: 1;
                }}
                100% {{
                    transform: scale(1.5);
                    opacity: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>Welcome to the Resource Explorer API</h1>
        <p>Explore the API documentation at <a href="{root_path}/docs">{root_path}/docs</a> or <a href="{root_path}/v1/docs">{root_path}/v1/docs</a>.</p>
        <div class="cursor" id="cursor"></div>
        <script>
            const cursor = document.getElementById('cursor');
            document.addEventListener('mousemove', (e) => {{
                cursor.style.left = e.pageX + 'px';
                cursor.style.top = e.pageY + 'px';
            }});
        </script>
    </body>
    </html>
    """

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)