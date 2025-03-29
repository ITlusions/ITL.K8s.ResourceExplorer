import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse

router = APIRouter()

root_path = os.getenv("ROOT_PATH", "/resource-explorer")

# Basic Health Check (Liveness Probe)
@router.get("/health", status_code=200, tags=["Health"])
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)

# Readiness Check
@router.get("/readiness", status_code=200, tags=["Health"])
async def readiness_check():
    try:
        # Simulated checks
        database_connected = True  # Replace with actual database connection check
        external_service_available = True  # Replace with external service check

        if database_connected and external_service_available:
            return JSONResponse(content={"status": "ready"}, status_code=200)
        else:
            return JSONResponse(content={"status": "not ready"}, status_code=503)

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "detail": str(e)}, status_code=503
        )

@router.get("/", response_class=HTMLResponse)
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