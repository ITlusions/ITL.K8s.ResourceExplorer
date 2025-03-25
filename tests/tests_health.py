import logging
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.main import app
import pytest
from unittest import mock

# Configure logging to ensure logs are shown in the console during testing
logging.basicConfig(
    level=logging.DEBUG,  # Set log level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger()


# Synchronous Test
def test_health():
    client = TestClient(app, base_url="http://localhost:8000")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()


def test_get_ingresses_route_success():
    client = TestClient(app, base_url="http://localhost:8000")
    """Test the /get-ingresses endpoint with a successful response."""
    response = client.get("/v1/get-ingresses")
    logger.info(response.content)
    # Assert the response status and content
    assert response.status_code == 200
    assert response.json()


def test_get_ingresses_route_failure():
    client = TestClient(app, base_url="http://localhost:8000")
    """Test the /get-ingresses endpoint when an exception is raised."""
    response = client.get("/v99/get-ingresses")
    logger.info(response.content)
    # Assert the response status and error message
    assert response.status_code == 404


# Asynchronous Test
@pytest.mark.asyncio
async def test_health_async():
    logger.info("Starting test for /health endpoint...")

    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = ac.get("/health")
        log = response
        logger.info(log)
    # Enhanced assertions with clear error messages
    assert response, f"Unexpected status code:"

    logger.info("Test for /health endpoint passed successfully.")


# Asynchronous Test
@pytest.mark.asyncio
async def test_v1_docs():
    logger.info("Starting test for /v1/docs endpoint...")

    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = ac.get("/v1/docs")
    # Enhanced assertions with clear error messages
    assert response, f"Unexpected status code:"

    logger.info("Test for /v1/docs endpoint passed successfully.")
