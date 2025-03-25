from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


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
