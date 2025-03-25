from fastapi import HTTPException
from typing import Optional, Callable
from pydantic import BaseModel


async def fetch_services_and_ingresses(
    controller_get_services: Callable[[Optional[str], Optional[str]], list],
    controller_get_ingresses: Callable[[], list],
    DiscoveredServices: BaseModel,
    annotation_key: Optional[str] = None,
    annotation_value: Optional[str] = None,
):
    """Generic helper function to fetch services and ingresses."""
    try:
        services = await controller_get_services(
            annotation_key=annotation_key, annotation_value=annotation_value
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching services: {str(e)}"
        )

    try:
        ingresses = await controller_get_ingresses()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"Error fetching ingresses: {str(e)}"
        )

    return DiscoveredServices(services=services, ingresses=ingresses)
