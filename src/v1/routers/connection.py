from fastapi import APIRouter
from v1.models.models import ConnectionRequest
from v1.controllers.connection import test_connection

router = APIRouter(prefix="/connection", tags=["Connection"])

@router.post("/test")
def test_connection_endpoint(request: ConnectionRequest):
    """
    Endpoint to test a connection to a host and port.
    """
    return test_connection(host=request.host, port=request.port)