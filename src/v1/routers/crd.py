from fastapi import APIRouter
from v1.controllers.crd import (
    list_crds as controller_list_crds, 
    get_crd_items as controller_get_crd_items,
    create_dynamic_crd_functions as controller_create_dynamic_crd_functions
)
from v1.models.models import CRDItemRequest

router = APIRouter(prefix="/crds", tags=["K8s Resources"])

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

# Dynamically create and add CRD routes
for function_name, function in controller_create_dynamic_crd_functions().items():
    if function_name.startswith("list_"):
        if "namespace" in function.__code__.co_varnames:
            # Namespaced CRD
            router.add_api_route(
                f"/{function_name[5:]}/{{namespace}}",
                function,
                methods=["GET"],
                name=f"List {function_name[5:]}",
                response_model=dict,
            )
        else:
            # Non-namespaced CRD
            router.add_api_route(
                f"/{function_name[5:]}",
                function,
                methods=["GET"],
                name=f"List {function_name[5:]}",
                response_model=dict,
            )
    elif function_name.startswith("get_"):
        if "namespace" in function.__code__.co_varnames:
            # Namespaced CRD
            router.add_api_route(
                f"/{function_name[4:]}/{{namespace}}/{{name}}",
                function,
                methods=["GET"],
                name=f"Get {function_name[4:]}",
                response_model=dict,
            )
        else:
            # Non-namespaced CRD
            router.add_api_route(
                f"/{function_name[4:]}/{{name}}",
                function,
                methods=["GET"],
                name=f"Get {function_name[4:]}",
                response_model=dict,
            )