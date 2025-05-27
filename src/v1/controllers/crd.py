from fastapi import HTTPException
from kubernetes import client
from kubernetes.client.exceptions import ApiException
from base.k8s_config import load_k8s_config
from base.utils import mask_secrets
import logging

logger = logging.getLogger(__name__)

class CRDManager:
    def __init__(self):
        """
        Initialize the CRDManager by loading Kubernetes configurations
        and setting up API clients.
        """
        load_k8s_config()
        self.api_extension_client = client.ApiextensionsV1Api()
        self.custom_objects_api = client.CustomObjectsApi()

    def list_crds(self):
        """
        List all Custom Resource Definitions (CRDs) in the cluster.
        """
        try:
            crds = self.api_extension_client.list_custom_resource_definition()
            return [{"name": crd.metadata.name, "group": crd.spec.group, "version": crd.spec.versions[0].name} for crd in crds.items]
        except ApiException as e:
            logger.error(f"Error fetching CRDs: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching CRDs: {str(e)}")

    def get_crd_items(self, group: str, version: str, plural: str, namespace: str = None):
        """
        Get items from a specific CRD.

        Args:
            group (str): The API group of the CRD.
            version (str): The version of the CRD.
            plural (str): The plural name of the CRD (e.g., "customresources").
            namespace (str, optional): The namespace to query (if the CRD is namespaced).

        Returns:
            dict: A dictionary of items from the specified CRD with sensitive information masked.
        """
        try:
            if namespace:
                items = self.custom_objects_api.list_namespaced_custom_object(
                    group=group,
                    version=version,
                    namespace=namespace,
                    plural=plural,
                )
            else:
                items = self.custom_objects_api.list_cluster_custom_object(
                    group=group,
                    version=version,
                    plural=plural,
                )
            # Mask sensitive information
            return mask_secrets(items)
        except ApiException as e:
            logger.error(f"Error fetching CRD items: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching CRD items: {str(e)}")

    def create_dynamic_crd_functions(self):
        """
        Dynamically create functions for each CRD to list and get items,
        separating namespaced and non-namespaced CRDs. The function names
        will use the group name instead of the plural name.
        """
        try:
            # Fetch all CRDs
            crds = self.api_extension_client.list_custom_resource_definition()

            # Dictionary to store dynamically created functions
            crd_functions = {}

            for crd in crds.items:
                group = crd.spec.group
                version = crd.spec.versions[0].name
                plural = crd.spec.names.plural
                namespaced = crd.spec.scope == "Namespaced"

                # Generate a unique identifier for the CRD using group and plural
                group_identifier = group.replace(".", "_")  # Replace dots with underscores for valid function names

                if namespaced:
                    # Create a function to list items for the namespaced CRD
                    def list_items(namespace: str, group=group, version=version, plural=plural):
                        return self.get_crd_items(group=group, version=version, plural=plural, namespace=namespace)

                    # Create a function to get a specific item for the namespaced CRD
                    def get_item(namespace: str, name: str, group=group, version=version, plural=plural):
                        items = self.get_crd_items(group=group, version=version, plural=plural, namespace=namespace)
                        return next((item for item in items.get("items", []) if item["metadata"]["name"] == name), None)

                    # Add the functions to the dictionary
                    crd_functions[f"list_{group_identifier}_{plural}"] = list_items
                    crd_functions[f"get_{group_identifier}_{plural}"] = get_item

                else:
                    # Create a function to list items for the cluster-scoped CRD
                    def list_items(group=group, version=version, plural=plural):
                        return self.get_crd_items(group=group, version=version, plural=plural)

                    # Create a function to get a specific item for the cluster-scoped CRD
                    def get_item(name: str, group=group, version=version, plural=plural):
                        items = self.get_crd_items(group=group, version=version, plural=plural)
                        return next((item for item in items.get("items", []) if item["metadata"]["name"] == name), None)

                    # Add the functions to the dictionary
                    crd_functions[f"list_{group_identifier}_{plural}"] = list_items
                    crd_functions[f"get_{group_identifier}_{plural}"] = get_item

            return crd_functions

        except ApiException as e:
            logger.error(f"Error creating dynamic CRD functions: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating dynamic CRD functions: {str(e)}")