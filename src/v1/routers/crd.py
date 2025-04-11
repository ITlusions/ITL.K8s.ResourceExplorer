from fastapi import APIRouter
from v1.controllers.crd import CRDManager
from v1.models.models import CRDItemRequest
from pydantic import BaseModel, create_model
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/crds", tags=["K8s Resources"])

@router.get("/list-crds")
def list_crds():
    """
    API endpoint to list all Custom Resource Definitions (CRDs).
    """
    return CRDManager.list_crds()

@router.post("/items")
def get_items_from_crd(request: CRDItemRequest):
    """
    API endpoint to get items from a specific CRD.
    """
    return CRDManager.get_crd_items(
        group=request.group,
        version=request.version,
        plural=request.plural,
        namespace=request.namespace,
    )

# Dynamically create and add CRD routes
crd_manager = CRDManager()
for group_name, function in crd_manager.create_dynamic_crd_functions().items():
    # Dynamically create a generic model for each CRD
    crd_model_name = f"{group_name.capitalize()}Model"
    crd_model = create_model(
        crd_model_name,
        apiVersion=(Optional[str], None),
        kind=(Optional[str], None),
        metadata=(Optional[Dict[str, Any]], None),
        items=(Optional[List[Dict[str, Any]]], None),
        group=(Optional[str], None),
        version=(Optional[str], None),
        plural=(Optional[str], None),
        __base__=BaseModel,
    )

    plural = function.__annotations__.get("plural", group_name[5:] if group_name.startswith("list_") else group_name[4:])

    if group_name.startswith("list_"):
        if "namespace" in function.__code__.co_varnames:
            # Namespaced CRD
            router.add_api_route(
                f"/{plural}/{{namespace}}",
                function,
                methods=["GET"],
                name=f"List {plural}",
                response_model=crd_model,
            )
        else:
            # Non-namespaced CRD
            router.add_api_route(
                f"/{plural}",
                function,
                methods=["GET"],
                name=f"List {plural}",
                response_model=crd_model,
            )
    elif group_name.startswith("get_"):
        if "namespace" in function.__code__.co_varnames:
            # Namespaced CRD
            router.add_api_route(
                f"/{plural}/{{namespace}}/{{name}}",
                function,
                methods=["GET"],
                name=f"Get {plural}",
                response_model=crd_model,
            )
        else:
            # Non-namespaced CRD
            router.add_api_route(
                f"/{plural}/{{name}}",
                function,
                methods=["GET"],
                name=f"Get {plural}",
                response_model=crd_model,
            )