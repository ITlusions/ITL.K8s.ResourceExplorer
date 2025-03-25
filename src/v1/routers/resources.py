from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from v1.controllers.resourceexplorer.controller import (
    get_namespaces as controller_get_namespaces,
    get_secrets as controller_get_secrets,
)
from v1.models.models import ExampleModel as ModelVoorbeeld

router = APIRouter()

@router.get(
    "/get-secrets"
)
async def get_secrets():

    return controller_get_secrets()

@router.get(
    "/get-namespaces"
)
async def get_namespaces():

    return controller_get_namespaces()

