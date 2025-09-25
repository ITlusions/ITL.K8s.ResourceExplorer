"""
Middleware for collecting Prometheus metrics.
"""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from base.metrics import metrics
from typing import Callable

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for HTTP requests."""
    
    def __init__(self, app, app_name: str = "k8s-resource-explorer"):
        super().__init__(app)
        self.app_name = app_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process HTTP request and collect metrics."""
        start_time = time.time()
        
        # Extract path and method
        method = request.method
        path = request.url.path
        
        # Clean up the path for metrics (remove IDs and sensitive info)
        clean_path = self._clean_path_for_metrics(path)
        
        try:
            # Process the request
            response = await call_next(request)
            status_code = response.status_code
            
            # Record successful request
            duration = time.time() - start_time
            metrics.record_http_request(method, clean_path, status_code, duration)
            
            return response
            
        except Exception as e:
            # Record failed request
            duration = time.time() - start_time
            metrics.record_http_request(method, clean_path, 500, duration)
            raise e
    
    def _clean_path_for_metrics(self, path: str) -> str:
        """Clean the path to remove variable parts for better metric grouping."""
        # Remove common variable patterns
        cleaned_path = path
        
        # Replace UUIDs, IDs, and other variable parts with placeholders
        import re
        
        # Replace UUIDs
        cleaned_path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 
            '/{uuid}', 
            cleaned_path
        )
        
        # Replace numeric IDs
        cleaned_path = re.sub(r'/\d+', '/{id}', cleaned_path)
        
        # Replace common Kubernetes resource names (but keep the pattern recognizable)
        cleaned_path = re.sub(r'/namespaces/[^/]+', '/namespaces/{namespace}', cleaned_path)
        cleaned_path = re.sub(r'/pods/[^/]+', '/pods/{pod}', cleaned_path)
        cleaned_path = re.sub(r'/services/[^/]+', '/services/{service}', cleaned_path)
        cleaned_path = re.sub(r'/deployments/[^/]+', '/deployments/{deployment}', cleaned_path)
        
        # Limit path depth to avoid too many unique metrics
        path_parts = cleaned_path.split('/')
        if len(path_parts) > 6:  # Adjust based on your API structure
            cleaned_path = '/'.join(path_parts[:6]) + '/...'
        
        return cleaned_path