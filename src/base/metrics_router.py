"""
Metrics router for Prometheus metrics endpoint.
"""

from fastapi import APIRouter, Response
from base.metrics import metrics
from prometheus_client import CONTENT_TYPE_LATEST

router = APIRouter()

@router.get("/metrics", include_in_schema=False)
async def get_metrics():
    """Prometheus metrics endpoint."""
    metrics_data = metrics.generate_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)

@router.get("/health/metrics", tags=["Health"])
async def get_metrics_health():
    """Health check for metrics endpoint."""
    try:
        # Try to generate metrics to ensure everything is working
        metrics.generate_metrics()
        return {
            "status": "healthy",
            "message": "Metrics collection is working properly"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": f"Metrics collection failed: {str(e)}"
        }