# Kubernetes Custom Resource Definitions (CRDs) API Routes

This module defines the API routes for managing Kubernetes Custom Resource Definitions (CRDs) and their associated resources. It leverages FastAPI's `APIRouter` to define and organize the routes.

## Routes

### Static Routes
- **`/list-crds` (GET)**: Lists all available CRDs by delegating to the `list_crds` controller function.
- **`/items` (POST)**: Retrieves items from a specific CRD based on the request payload, which includes the group, version, plural, and namespace of the CRD.

### Dynamically Generated Routes
- **Routes starting with `list_`**: Allow listing resources of a specific type within a namespace.
- **Routes starting with `get_`**: Allow retrieving a specific resource by name within a namespace.

## Dynamic Route Generation

The `controller_create_dynamic_crd_functions` function dynamically generates additional routes based on the available CRD resource types. These routes are added to the router at runtime.

### Dynamic Route Patterns
- **`/list_<resource_type>/{namespace}` (GET)**: Lists resources of the specified type in the given namespace.
- **`/get_<resource_type>/{namespace}/{name}` (GET)**: Retrieves a specific resource by name in the given namespace.

## Dependencies
- **`v1.controllers.crd`**: Contains the controller functions for handling CRD-related operations.
- **`v1.models.models`**: Defines the `CRDItemRequest` model used for request validation.

## Tags
- All routes are tagged with `K8s Resources` for better organization in the API documentation.