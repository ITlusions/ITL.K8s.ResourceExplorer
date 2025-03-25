import uuid
import os
import socket
import time
import logging
import re
import asyncio
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from collections import OrderedDict

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit")

class CorrelationStore:
    """Manages correlation IDs, validation, and periodic cleanup."""
    UUID_PATTERN = re.compile(
        r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
        re.IGNORECASE
    )

    def __init__(self, max_ids=1000, max_age=300, cleanup_interval=60, log_interval=60):
        self.store = OrderedDict()
        self.max_ids = max_ids
        self.max_age = max_age  # in seconds
        self.cleanup_interval = cleanup_interval
        self.log_interval = log_interval  # Interval for logging
        self._cleanup_task = None
        self._log_task = None  # Task for periodic logging
        self._lock = asyncio.Lock()

    def start_cleanup_task(self):
        """Start the background cleanup task and log task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
        if self._log_task is None:
            self._log_task = asyncio.create_task(self._periodic_log())

    async def _background_cleanup(self):
        """Background process for periodic cleanup."""
        while True:
            await asyncio.sleep(self.cleanup_interval)
            await self.cleanup()

    async def _periodic_log(self):
        """Background process for periodic logging of the correlation store."""
        while True:
            await asyncio.sleep(self.log_interval)
            await self.log_correlation_store()

    async def log_correlation_store(self):
        """Log the current state of the correlation store."""
        async with self._lock:
            current_time = time.time()
            logger.info({
                "event": "correlation_store_snapshot",
                "timestamp": current_time,
                "total_entries": len(self.store),
                "store": list(self.store.items())  # Log the entire store
            })

    async def validate_uuid(self, value: str) -> str:
        """Validate UUID or generate a new one if invalid."""
        return value if self.UUID_PATTERN.match(value) else str(uuid.uuid4())

    async def add_request(self, correlation_id: str, request_id: str):
        """Add request to the store."""
        async with self._lock:
            timestamp = time.time()
            self.store.setdefault(correlation_id, (timestamp, []))[1].append(request_id)

    async def cleanup(self):
        """Remove old or excess correlation IDs."""
        async with self._lock:
            current_time = time.time()

            # Remove old entries
            for cid in list(self.store.keys()):
                ts, _ = self.store[cid]
                if current_time - ts > self.max_age:
                    del self.store[cid]

            # Remove oldest entries if the maximum number of entries is exceeded
            while len(self.store) > self.max_ids:
                self.store.popitem(last=False)

    async def get_request_count(self, correlation_id: str) -> int:
        """Get the request count for a correlation ID."""
        async with self._lock:
            return len(self.store.get(correlation_id, (None, []))[1])

    async def find_existing_correlation(self, client_ip: str, url: str) -> str:
        """Find existing correlation ID for identical requests (same IP and URL)."""
        async with self._lock:
            for cid, (_, requests) in self.store.items():
                for req_id in requests:
                    if req_id.startswith(f"{client_ip}-{url}"):
                        return cid
            return None

# Create a global instance and start the background cleanup and log tasks
correlation_store = CorrelationStore()
correlation_store.start_cleanup_task()

class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware voor audit logging en correlation tracking."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        request_id = str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID")

        if not correlation_id:
            # Geen correlation_id meegegeven, probeer een bestaande te vinden op basis van client IP en URL
            client_ip = (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or request.headers.get("X-Real-IP")
                or (request.client.host if request.client else "unknown")
            )
            url = str(request.url)
            correlation_id = await correlation_store.find_existing_correlation(client_ip, url)

            if not correlation_id:
                # Geen bestaande correlation_id, maak een nieuwe
                correlation_id = str(uuid.uuid4())

        # Registreer de request in de correlation store
        await correlation_store.add_request(correlation_id, request_id)

        hostname = socket.gethostname()
        version = os.getenv("APP_VERSION", "unknown")

        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or request.headers.get("X-Real-IP")
            or (request.client.host if request.client else "unknown")
        )

        try:
            response = await call_next(request)
        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"Request failed: {e}", exc_info=True)
            response = Response(
                "Internal server error", status_code=HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            duration = time.perf_counter() - start_time
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Server-Hostname"] = hostname
            response.headers["X-App-Version"] = version

            # Log details
            stored_requests = await correlation_store.get_request_count(correlation_id)
            logger.info({
                "event": "request",
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "request_id": request_id,
                "correlation_id": correlation_id,
                "duration": f"{duration:.3f}s",
                "status_code": response.status_code,
                "stored_requests": stored_requests
            })

        return response
