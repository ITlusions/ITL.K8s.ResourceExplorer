"""
Prometheus metrics for K8s Resource Explorer application.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry, multiprocess, REGISTRY
import time
import os
import psutil
from typing import Optional

class PrometheusMetrics:
    """Prometheus metrics collector for the application."""
    
    def __init__(self):
        """Initialize Prometheus metrics."""
        
        # HTTP Request metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        # API Key authentication metrics
        self.auth_attempts_total = Counter(
            'auth_attempts_total',
            'Total authentication attempts',
            ['status']  # success, failure, invalid_key
        )
        
        # Kubernetes API metrics
        self.k8s_api_requests_total = Counter(
            'k8s_api_requests_total',
            'Total Kubernetes API requests',
            ['resource_type', 'action', 'namespace', 'status']
        )
        
        self.k8s_api_request_duration_seconds = Histogram(
            'k8s_api_request_duration_seconds',
            'Kubernetes API request duration in seconds',
            ['resource_type', 'action']
        )
        
        # Resource metrics
        self.k8s_resources_discovered = Gauge(
            'k8s_resources_discovered',
            'Number of Kubernetes resources discovered',
            ['resource_type', 'namespace']
        )
        
        # Application metrics
        self.app_info = Gauge(
            'app_info',
            'Application information',
            ['version', 'environment', 'namespace']
        )
        
        # System metrics
        self.process_memory_bytes = Gauge(
            'process_memory_bytes',
            'Process memory usage in bytes'
        )
        
        self.process_cpu_usage = Gauge(
            'process_cpu_usage',
            'Process CPU usage percentage'
        )
        
        # Active connections
        self.active_connections = Gauge(
            'active_connections',
            'Number of active connections'
        )
        
        # Initialize application info
        self.set_app_info()
        
    def set_app_info(self):
        """Set application information metrics."""
        version = os.getenv('APP_VERSION', 'unknown')
        environment = os.getenv('ENVIRONMENT', 'development')
        namespace = os.getenv('KUBERNETES_NAMESPACE', 'default')
        
        self.app_info.labels(
            version=version,
            environment=environment,
            namespace=namespace
        ).set(1)
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_auth_attempt(self, status: str):
        """Record authentication attempt.
        
        Args:
            status: 'success', 'failure', or 'invalid_key'
        """
        self.auth_attempts_total.labels(status=status).inc()
    
    def record_k8s_request(self, resource_type: str, action: str, namespace: str, 
                          status: str, duration: Optional[float] = None):
        """Record Kubernetes API request metrics.
        
        Args:
            resource_type: Type of Kubernetes resource (pods, services, etc.)
            action: Action performed (list, get, create, delete, etc.)
            namespace: Kubernetes namespace
            status: Request status (success, error, timeout)
            duration: Request duration in seconds
        """
        self.k8s_api_requests_total.labels(
            resource_type=resource_type,
            action=action,
            namespace=namespace,
            status=status
        ).inc()
        
        if duration is not None:
            self.k8s_api_request_duration_seconds.labels(
                resource_type=resource_type,
                action=action
            ).observe(duration)
    
    def update_resource_count(self, resource_type: str, namespace: str, count: int):
        """Update the count of discovered resources."""
        self.k8s_resources_discovered.labels(
            resource_type=resource_type,
            namespace=namespace
        ).set(count)
    
    def update_system_metrics(self):
        """Update system-level metrics."""
        process = psutil.Process()
        
        # Memory usage
        memory_info = process.memory_info()
        self.process_memory_bytes.set(memory_info.rss)
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        self.process_cpu_usage.set(cpu_percent)
    
    def set_active_connections(self, count: int):
        """Set the number of active connections."""
        self.active_connections.set(count)
    
    def generate_metrics(self) -> str:
        """Generate Prometheus metrics in text format."""
        # Update system metrics before generating
        self.update_system_metrics()
        
        return generate_latest(REGISTRY).decode('utf-8')

# Global metrics instance
metrics = PrometheusMetrics()