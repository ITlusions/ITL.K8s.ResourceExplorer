from kubernetes import config, client
import os


def load_k8s_config():
    """Load Kubernetes configuration."""
    try:
        # Try to load the in-cluster config (for running inside Kubernetes)
        config.load_incluster_config()
        print("Loaded in-cluster Kubernetes config.")
    except config.ConfigException:
        # Fallback to local kubeconfig file (for local development)
        kubeconfig_path = os.getenv(
            "KUBECONFIG", "~/.kube/config"
        )  # Default to ~/.kube/config if not set
        config.load_kube_config(config_file=kubeconfig_path)
        print(f"Loaded kubeconfig from {kubeconfig_path}")