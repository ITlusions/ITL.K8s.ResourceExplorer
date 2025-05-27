from fastapi import APIRouter, HTTPException
from v1.controllers.crd import CRDManager
from v1.models.models import CRDItemRequest
from pydantic import BaseModel, create_model
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/crds", tags=["Custom Resources"])

@router.get("/")
def list_crds():
    """
    API endpoint to list all Custom Resource Definitions (CRDs).
    """
    crd_manager = CRDManager()
    return crd_manager.list_crds()

@router.post("/items")
def get_items_from_crd(request: CRDItemRequest):
    """
    API endpoint to get items from a specific CRD.
    """
    crd_manager = CRDManager()

    return crd_manager.get_crd_items(
        group=request.group,
        version=request.version,
        plural=request.plural,
        namespace=request.namespace,
    )

@router.get("/{group}/{version}/{plural}/{namespace}")
def list_namespaced_crd_items(group: str, version: str, plural: str, namespace: str):
    """
    List items from a namespaced CRD.
    """
    return crd_manager.get_crd_items(group=group, version=version, plural=plural, namespace=namespace)

@router.get("/{group}/{version}/{plural}/{namespace}/{name}")
def get_namespaced_crd_item(group: str, version: str, plural: str, namespace: str, name: str):
    """
    Get a specific item from a namespaced CRD.
    """
    items = crd_manager.get_crd_items(group=group, version=version, plural=plural, namespace=namespace)
    return next((item for item in items.get("items", []) if item["metadata"]["name"] == name), None)

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