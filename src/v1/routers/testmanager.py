from fastapi import APIRouter, Depends, HTTPException
from v1.managers.testmanager import TestManager
from v1.interfaces.resourcemanager import TestManagerInterface

router = APIRouter(prefix="/test", tags=["Test"])

# Dependency injection for the test manager
def get_test_manager() -> TestManagerInterface:
    return TestManager()

@router.get("/smtp", response_model=dict)
async def test_smtp(
    host: str,
    use_starttls: bool = False,
    test_manager: TestManagerInterface = Depends(get_test_manager)
):
    """
    API endpoint to test SMTP connectivity.
    """
    try:
        result = await test_manager.test_smtp(host, use_starttls=use_starttls)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dns", response_model=dict)
async def test_dns(host: str, test_manager: TestManagerInterface = Depends(get_test_manager)):
    """
    API endpoint to test DNS resolution.
    """
    try:
        result = await test_manager.test_dns(host)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))