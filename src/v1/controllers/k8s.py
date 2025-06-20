import asyncio
import base64
import yaml
import os
from datetime import datetime
from fastapi import HTTPException, WebSocket
from kubernetes import client
from fastapi import HTTPException
from kubernetes import client, watch, config, stream
from kubernetes.client.exceptions import ApiException
from base.k8s_config import load_k8s_config
from typing import Optional
from v1.models.models import PersistentVolume, PersistentVolumeClaim, StorageClass
import traceback
import logging

# Load Kubernetes Configurations
load_k8s_config()

core_v1_api = client.CoreV1Api()
apps_v1_api = client.AppsV1Api()
apis_api = client.ApisApi()
networking_v1_api = client.NetworkingV1Api()
storage_v1_api = client.StorageV1Api()

def get_all_resource_types():
    """
    Fetch all available resource types in the Kubernetes cluster.
    """
    try:
        # Fetch core API resources
        core_resources = core_v1_api.get_api_resources()
        core_resource_types = [
            {"name": resource.name, "kind": resource.kind, "namespaced": resource.namespaced}
            for resource in core_resources.resources
        ]

        # Fetch resources from all API groups
        api_groups = apis_api.get_api_versions()
        group_resource_types = []
        for group in api_groups.groups:
            for version in group.versions:
                group_version = f"{group.name}/{version.version}" if group.name else version.version
                try:
                    group_resources = client.ApiClient().call_api(
                        f"/apis/{group_version}", "GET", response_type="V1APIResourceList"
                    )
                    group_resource_types.extend([
                        {
                            "name": resource.name,
                            "kind": resource.kind,
                            "namespaced": resource.namespaced,
                            "groupVersion": group_version,
                        }
                        for resource in group_resources.resources
                    ])
                except Exception:
                    continue

        # Combine core and group resources
        all_resource_types = core_resource_types + group_resource_types

        return {"resource_types": all_resource_types}

    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resource types: {str(e)}")

async def describe_resource(namespace: str, resource_type: str, resource_name: str):
    try:
        if resource_type == "pod":
            resource = core_v1_api.read_namespaced_pod(name=resource_name, namespace=namespace)
        elif resource_type == "service":
            resource = core_v1_api.read_namespaced_service(name=resource_name, namespace=namespace)
        elif resource_type == "deployment":
            resource = apps_v1_api.read_namespaced_deployment(name=resource_name, namespace=namespace)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported resource type: {resource_type}")

        if not resource:
            raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()} '{resource_name}' not found in namespace '{namespace}'")

        return {
            "metadata": resource.metadata.to_dict(),
            "spec": resource.spec.to_dict(),
            "status": resource.status.to_dict(),
        }
    except ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"{resource_type.capitalize()} '{resource_name}' not found in namespace '{namespace}'")
        raise HTTPException(status_code=500, detail=f"Error fetching resource: {str(e)}")

async def list_resources_grouped_by_namespace():
    """
    Fetch all resources (pods, services, deployments) grouped by namespace.
    """
    try:
        namespaces = core_v1_api.list_namespace().items
        result = {}

        for ns in namespaces:
            namespace_name = ns.metadata.name

            # Fetch resources in the namespace
            pods = core_v1_api.list_namespaced_pod(namespace=namespace_name).items
            services = core_v1_api.list_namespaced_service(namespace=namespace_name).items
            deployments = apps_v1_api.list_namespaced_deployment(namespace=namespace_name).items

            # Group resources by namespace
            result[namespace_name] = {
                "pods": [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods],
                "services": [{"name": svc.metadata.name, "type": svc.spec.type} for svc in services],
                "deployments": [{"name": dep.metadata.name, "replicas": dep.status.replicas} for dep in deployments],
            }

        return result
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching resources: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def stream_kubernetes_events():
    """
    Stream Kubernetes events in real-time.
    """
    v1 = client.CoreV1Api()
    w = watch.Watch()

    try:
        # Watch events in the cluster
        loop = asyncio.get_event_loop()
        for event in await loop.run_in_executor(None, lambda: w.stream(core_v1_api.list_event_for_all_namespaces, timeout_seconds=5)):
            # Format the event as a Server-Sent Event (SSE)
            event_type = event.get("type", "UNKNOWN")
            event_object = event.get("object", {})
            event_name = getattr(event_object.metadata, "name", "UNKNOWN")
            event_message = getattr(event_object, "message", "No message available")
            yield f"data: {event_type} - {event_name} - {event_message}\n\n"
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"
    finally:
        w.stop()

async def list_ingresses(namespace: str) -> list:
    """
    Retrieves a list of Ingresses in the specified namespace.

    Args:
        namespace (str): The namespace to query for Ingresses.

    Returns:
        list: A list of Ingress objects in the specified namespace.
    """
    try:
        # List Ingresses in the specified namespace
        ingresses = networking_v1_api.list_namespaced_ingress(namespace=namespace)

        # Extract relevant information from the Ingress objects
        ingress_list = [
            {
                "name": ingress.metadata.name,
                "namespace": ingress.metadata.namespace,
                "host": ingress.spec.rules[0].host if ingress.spec.rules else None,
                "paths": [
                    path.path for path in ingress.spec.rules[0].http.paths
                ] if ingress.spec.rules and ingress.spec.rules[0].http else [],
                "creation_timestamp": ingress.metadata.creation_timestamp,
            }
            for ingress in ingresses.items
        ]

        return ingress_list

    except ApiException as e:
        raise ApiException(f"Error retrieving Ingresses in namespace '{namespace}': {e.reason}")

async def list_nodes() -> list:
    """
    Retrieves a list of all Nodes in the Kubernetes cluster, including their status and resource usage.

    Returns:
        list: A list of Node objects with relevant details.
    """
    try:

        # List all nodes in the cluster
        nodes = core_v1_api.list_node()

        # Extract relevant information from the Node objects
        node_list = [
            {
                "name": node.metadata.name,
                "status": "Ready" if any(
                    condition.type == "Ready" and condition.status == "True"
                    for condition in node.status.conditions
                ) else "NotReady",
                "capacity": node.status.capacity,
                "allocatable": node.status.allocatable,
                "labels": node.metadata.labels,
                "creation_timestamp": node.metadata.creation_timestamp,
            }
            for node in nodes.items
        ]

        return node_list

    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error retrieving nodes: {e.reason}")

async def controller_list_storage_classes() -> list[StorageClass]:
    """
    Controller to list all StorageClasses in the Kubernetes cluster.
    """
    try:
        storage_classes = storage_v1_api.list_storage_class()
        return [
            StorageClass(
                name=sc.metadata.name,
                namespace=None,
                message="StorageClass retrieved successfully",
                reason=None,
                timestamp=sc.metadata.creation_timestamp.isoformat() if sc.metadata.creation_timestamp else None,
            )
            for sc in storage_classes.items
        ]
    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching StorageClasses: {e.reason}")

async def interactive_exec(websocket: WebSocket, namespace: str, pod_name: str, container_name: str):
    """
    Controller to handle interactive WebSocket streaming to a Kubernetes container.
    """
    try:

        # Define the command to start a shell
        exec_command = ["/bin/sh"]

        # Open a WebSocket stream to the Kubernetes API
        resp = stream.stream(
            core_v1_api.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            container=container_name,
            command=exec_command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=True,
            _preload_content=False,  # Disable automatic content processing
        )

        # Accept the WebSocket connection
        await websocket.accept()

        # Read and write data between the client and the Kubernetes pod
        while resp.is_open():
            # Read data from the Kubernetes stream
            if resp.peek_stdout():
                output = resp.read_stdout()
                await websocket.send_text(output)

            if resp.peek_stderr():
                error = resp.read_stderr()
                await websocket.send_text(error)

            # Read data from the WebSocket client
            data = await websocket.receive_text()
            resp.write_stdin(data)

        resp.close()
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))

async def list_pvcs(namespace: Optional[str] = None) -> list[PersistentVolumeClaim]:
    """
    List PersistentVolumeClaims (PVCs) in the Kubernetes cluster.
    If a namespace is provided, list PVCs only in that namespace.
    """
    try:
        if namespace:
            pvcs = core_v1_api.list_namespaced_persistent_volume_claim(namespace=namespace)
        else:
            pvcs = core_v1_api.list_persistent_volume_claim_for_all_namespaces()

        return [
            PersistentVolumeClaim(
                name=pvc.metadata.name,
                namespace=pvc.metadata.namespace,
                status=pvc.status.phase,
                storage=pvc.status.capacity.get("storage") if pvc.status.capacity else None,
                access_modes=pvc.spec.access_modes,
                storage_class=pvc.spec.storage_class_name,
            )
            for pvc in pvcs.items
        ]
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching PVCs: {e.reason}")

async def list_pvs(namespace: Optional[str] = None) -> list[PersistentVolume]:
    """
    List PersistentVolumes (PVs) in the Kubernetes cluster.
    If a namespace is provided, filter PVs by their claimRef namespace.
    """
    try:
        pvs = core_v1_api.list_persistent_volume()

        # Filter PVs by namespace if provided
        filtered_pvs = [
            pv for pv in pvs.items
            if not namespace or (pv.spec.claim_ref and pv.spec.claim_ref.namespace == namespace)
        ]

        return [
            PersistentVolume(
                name=pv.metadata.name,
                status=pv.status.phase,
                capacity=pv.spec.capacity.get("storage") if pv.spec.capacity else None,
                access_modes=pv.spec.access_modes,
                reclaim_policy=pv.spec.persistent_volume_reclaim_policy,
                storage_class=pv.spec.storage_class_name,
                volume_mode=pv.spec.volume_mode,
            )
            for pv in filtered_pvs
        ]
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching PVs: {e.reason}")

def generate_kubeconfig(service_account_name: str, namespace: str, output_file: str = "kubeconfig.yaml") -> str:
    """
    Generate a kubeconfig file for a specific service account.

    Args:
        service_account_name (str): The name of the service account.
        namespace (str): The namespace where the service account is located.
        output_file (str): The file path to save the generated kubeconfig.

    Returns:
        str: The path to the generated kubeconfig file.

    Raises:
        HTTPException: If the service account or related resources cannot be retrieved.
    """
    try:
        # Load Kubernetes configuration
        config.load_kube_config()  # Use load_incluster_config() if running inside a cluster

        # Create API clients
        core_v1_api = client.CoreV1Api()

        # Get the service account
        service_account = core_v1_api.read_namespaced_service_account(
            name=service_account_name, namespace=namespace
        )

        # Get the secret associated with the service account
        if not service_account.secrets:
            raise HTTPException(
                status_code=404,
                detail=f"Service account '{service_account_name}' does not have an associated secret."
            )
        
        secret_name = service_account.secrets[0].name
        secret = core_v1_api.read_namespaced_secret(name=secret_name, namespace=namespace)

        # Extract the token, CA certificate, and API server endpoint
        token = secret.data["token"]
        ca_cert = secret.data["ca.crt"]
        api_server = config.kube_config.Configuration().host

        # Decode the token and CA certificate
        token = base64.b64decode(token).decode("utf-8")
        ca_cert = base64.b64decode(ca_cert).decode("utf-8")

        # Create the kubeconfig content
        kubeconfig = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "name": "kubernetes",
                    "cluster": {
                        "certificate-authority-data": ca_cert,
                        "server": api_server,
                    },
                }
            ],
            "contexts": [
                {
                    "name": "default",
                    "context": {
                        "cluster": "kubernetes",
                        "user": service_account_name,
                        "namespace": namespace,
                    },
                }
            ],
            "current-context": "default",
            "users": [
                {
                    "name": service_account_name,
                    "user": {
                        "token": token,
                    },
                }
            ],
        }

        # Write the kubeconfig to a file
        with open(output_file, "w") as f:
            yaml.dump(kubeconfig, f)

        return output_file

    except ApiException as e:
        raise HTTPException(
            status_code=e.status if e.status else 500,
            detail=f"Failed to generate kubeconfig: {e.reason if e.reason else str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

async def list_service_accounts_and_kubeconfigs(namespace: str) -> dict:
    """
    List all service accounts in a namespace and generate kubeconfigs for each.

    Args:
        namespace (str): The namespace to list service accounts from.

    Returns:
        dict: A dictionary containing service account names and their kubeconfig content.

    Raises:
        HTTPException: If an error occurs while fetching service accounts or generating kubeconfigs.
    """
    try:
        # List all service accounts in the namespace
        service_accounts = core_v1_api.list_namespaced_service_account(namespace=namespace).items

        result = {}
        for sa in service_accounts:
            sa_name = sa.metadata.name

            # Generate kubeconfig for the service account
            kubeconfig = generate_kubeconfig_as_dict(service_account_name=sa_name, namespace=namespace)

            result[sa_name] = kubeconfig

        return result

    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Error fetching service accounts: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def generate_kubeconfig_as_dict(service_account_name: str, namespace: str) -> dict:
    """
    Generate a kubeconfig for a specific service account and return it as a dictionary.

    Args:
        service_account_name (str): The name of the service account.
        namespace (str): The namespace where the service account is located.

    Returns:
        dict: The kubeconfig content as a dictionary.

    Raises:
        Exception: If the service account or related resources cannot be retrieved.
    """
    try:
        # Load Kubernetes configuration
        config.load_kube_config()  # Use load_incluster_config() if running inside a cluster

        # Create API clients
        core_v1_api = client.CoreV1Api()

        # Get the service account
        service_account = core_v1_api.read_namespaced_service_account(
            name=service_account_name, namespace=namespace
        )

        # Get the secret associated with the service account
        if not service_account.secrets:
            raise Exception(f"Service account '{service_account_name}' does not have an associated secret.")
        
        secret_name = service_account.secrets[0].name
        secret = core_v1_api.read_namespaced_secret(name=secret_name, namespace=namespace)

        # Extract the token, CA certificate, and API server endpoint
        token = secret.data["token"]
        ca_cert = secret.data["ca.crt"]
        api_server = config.kube_config.Configuration().host

        # Decode the token and CA certificate
        token = base64.b64decode(token).decode("utf-8")
        ca_cert = base64.b64decode(ca_cert).decode("utf-8")

        # Create the kubeconfig content
        kubeconfig = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "name": "kubernetes",
                    "cluster": {
                        "certificate-authority-data": ca_cert,
                        "server": api_server,
                    },
                }
            ],
            "contexts": [
                {
                    "name": "default",
                    "context": {
                        "cluster": "kubernetes",
                        "user": service_account_name,
                        "namespace": namespace,
                    },
                }
            ],
            "current-context": "default",
            "users": [
                {
                    "name": service_account_name,
                    "user": {
                        "token": token,
                    },
                }
            ],
        }

        return kubeconfig

    except ApiException as e:
        raise Exception(f"Failed to generate kubeconfig: {e.reason}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {str(e)}")

def get_in_cluster_config() -> dict:
    """
    Retrieve the in-cluster Kubernetes configuration and return it as a kubeconfig dictionary.

    Returns:
        dict: A kubeconfig dictionary containing the API server endpoint, CA certificate, and token.

    Raises:
        HTTPException: If the in-cluster configuration cannot be loaded.
    """
    try:
        # Load in-cluster configuration
        config.load_incluster_config()

        # Read the service account token and CA certificate from the default paths
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as token_file:
            token = token_file.read().strip()

        with open("/var/run/secrets/kubernetes.io/serviceaccount/ca.crt", "r") as ca_file:
            ca_cert = ca_file.read().strip()

        # Get the API server endpoint
        api_server = config.kube_config.Configuration().host

        # Construct the kubeconfig dictionary
        kubeconfig = {
            "apiVersion": "v1",
            "kind": "Config",
            "clusters": [
                {
                    "name": "kubernetes",
                    "cluster": {
                        "certificate-authority-data": base64.b64encode(ca_cert.encode()).decode(),
                        "server": api_server,
                    },
                }
            ],
            "contexts": [
                {
                    "name": "default",
                    "context": {
                        "cluster": "kubernetes",
                        "user": "default",
                    },
                }
            ],
            "current-context": "default",
            "users": [
                {
                    "name": "default",
                    "user": {
                        "token": token,
                    },
                }
            ],
        }

        return kubeconfig

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve in-cluster configuration: {str(e)}")

async def get_storage_class(storage_class_name: str) -> dict:
    """
    Retrieve a specific StorageClass by name and return its full dictionary representation.

    Args:
        storage_class_name (str): The name of the StorageClass to retrieve.

    Returns:
        dict: The full dictionary representation of the StorageClass.

    Raises:
        HTTPException: If the StorageClass cannot be found or an error occurs.
    """
    try:
        # Retrieve the StorageClass by name
        storage_class = storage_v1_api.read_storage_class(name=storage_class_name)

        # Convert the StorageClass object to a dictionary
        return storage_class.to_dict()

    except ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"StorageClass '{storage_class_name}' not found.")
        raise HTTPException(status_code=e.status, detail=f"Error retrieving StorageClass: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

async def rollout_restart_deployment(namespace: str, deployment_name: str) -> dict:
    """
    Perform a rollout restart of a Kubernetes deployment.

    Args:
        namespace (str): The namespace of the deployment.
        deployment_name (str): The name of the deployment to restart.

    Returns:
        dict: A success message indicating the deployment was restarted.

    Raises:
        HTTPException: If the deployment cannot be found or an error occurs.
    """
    try:
        # Retrieve the deployment
        deployment = apps_v1_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)

        # Add or update an annotation to trigger a restart
        annotations = deployment.spec.template.metadata.annotations or {}
        annotations["kubectl.kubernetes.io/restartedAt"] = datetime.utcnow().isoformat()
        deployment.spec.template.metadata.annotations = annotations

        # Update the deployment
        apps_v1_api.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)

        return {"message": f"Deployment '{deployment_name}' in namespace '{namespace}' restarted successfully."}

    except client.exceptions.ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"Deployment '{deployment_name}' not found in namespace '{namespace}'.")
        raise HTTPException(status_code=e.status, detail=f"Error restarting deployment: {e.reason}")
    except Exception as e:
        error_details = traceback.format_exc()
        # Log the error details using a logger
        logger = logging.getLogger(__name__)
        logger.error(f"Error details: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}",
            headers={"X-Debug-Info": error_details}
        )

def create_cleanup_evicted_pods_job(namespace: str = "default", job_name: str = "cleanup-evicted-pods"):
    """
    Create a Kubernetes Job that deletes all evicted pods in the given namespace.
    """
    batch_v1 = client.BatchV1Api()
    # Get the service account name attached to the current pod (the API)
    service_account_name = os.environ.get("KUBERNETES_SERVICEACCOUNT", None)
    if not service_account_name:
        # Fallback to the default path used by Kubernetes for service account
        try:
            with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
                service_account_name = os.environ.get("KUBERNETES_SERVICE_ACCOUNT", "default")
        except Exception:
            service_account_name = "default"

    job_manifest = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": job_name, "namespace": namespace},
        "spec": {
            "template": {
                "metadata": {"name": job_name},
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [
                        {
                            "name": "cleanup-evicted-pods",
                            "image": "bitnami/kubectl:latest",
                            "command": [
                                "sh",
                                "-c",
                                "kubectl get pods --field-selector=status.phase=Failed -o name | grep Evicted | xargs -r kubectl delete"
                            ],
                        }
                    ],
                    "serviceAccountName": service_account_name,
                },
            }
        },
    }
    try:
        batch_v1.create_namespaced_job(namespace=namespace, body=job_manifest)
        return {"message": f"Cleanup job '{job_name}' created in namespace '{namespace}'."}
    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Failed to create cleanup job: {e.reason}")

def get_secret(namespace: str, secret_name: str) -> dict:
    """
    Retrieve a Kubernetes Secret and return its decoded values.
    """
    try:
        v1 = client.CoreV1Api()
        secret = v1.read_namespaced_secret(secret_name, namespace)
        decoded_data = {}
        for key, value in secret.data.items():
            decoded_data[key] = base64.b64decode(value).decode("utf-8")
        return {
            "name": secret.metadata.name,
            "namespace": secret.metadata.namespace,
            "data": decoded_data
        }
    except client.exceptions.ApiException as e:
        raise HTTPException(status_code=e.status, detail=f"Failed to get secret: {e.reason}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

