from fastapi import APIRouter, Depends
from v1.controllers.crd import list_crds, get_crd_items
from v1.models.models import CRDItemRequest

router = APIRouter(prefix="/crds", tags=["CRDs"])

@router.get("/list-crds", tags=["CRDs"])
def list_all_crds():
    """
    API endpoint to list all Custom Resource Definitions (CRDs).
    """
    return list_crds()

@router.post("/items", tags=["CRDs"])
def get_items_from_crd(request: CRDItemRequest):
    """
    API endpoint to get items from a specific CRD.
    """
    return get_crd_items(
        group=request.group,
        version=request.version,
        plural=request.plural,
        namespace=request.namespace,
    )