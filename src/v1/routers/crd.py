from fastapi import APIRouter
from v1.controllers.crd import (
    list_crds as controller_list_crds, 
    get_crd_items as controller_get_crd_items
)
from v1.models.models import CRDItemRequest

router = APIRouter(prefix="/crds", tags=["K8s"])

@router.get("/list-crds")
def list_crds():
    """
    API endpoint to list all Custom Resource Definitions (CRDs).
    """
    return controller_list_crds()

@router.post("/items")
def get_items_from_crd(request: CRDItemRequest):
    """
    API endpoint to get items from a specific CRD.
    """
    return controller_get_crd_items(
        group=request.group,
        version=request.version,
        plural=request.plural,
        namespace=request.namespace,
    )