from fastapi import APIRouter, HTTPException
from v1.controllers.crd import CRDManager
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

@router.get("/{group}/{version}/{plural}")
def list_crd_items(group: str, version: str, plural: str, namespace: Optional[str] = None):
    """
    List items from a CRD.
    """
    crd_manager = CRDManager()
    return crd_manager.get_crd_items(group=group, version=version, plural=plural, namespace=namespace)

@router.get("/{group}/{version}/{plural}/{namespace}/{name}")
def get_crd_item(group: str, version: str, plural: str, namespace: str, name: str):
    """
    Get a specific item from a CRD.
    """
    crd_manager = CRDManager()
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
                f"/{group_name}/{{version}}/{plural}/{{namespace}}",
                function,
                methods=["GET"],
                name=f"List {plural}",
                response_model=crd_model,
            )
        else:
            # Non-namespaced CRD
            router.add_api_route(
                f"/{group_name}/{{version}}/{plural}",
                function,
                methods=["GET"],
                name=f"List {plural}",
                response_model=crd_model,
            )
    elif group_name.startswith("get_"):
        if "namespace" in function.__code__.co_varnames:
            # Namespaced CRD
            router.add_api_route(
                f"/{group_name}/{{version}}/{plural}/{{namespace}}/{{name}}",
                function,
                methods=["GET"],
                name=f"Get {plural}",
                response_model=crd_model,
            )
        else:
            # Non-namespaced CRD
            router.add_api_route(
                f"/{group_name}/{{version}}/{plural}/{{name}}",
                function,
                methods=["GET"],
                name=f"Get {plural}",
                response_model=crd_model,
            )