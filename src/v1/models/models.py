from pydantic import BaseModel, field_validator, Field, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime
from base.utils import mask_secrets
from enum import Enum


class ResourceMetadata(BaseModel):
    name: str = Field(..., description="The name of the resource.")
    namespace: str = Field(..., description="The namespace of the resource.")
    creation_timestamp: datetime = Field(..., description="The creation timestamp of the resource.")


class ResourceDetail(BaseModel):
    metadata: ResourceMetadata
    spec: Dict[str, Any]
    status: Dict[str, Any]

    @field_validator("spec", "status", mode="before")
    def mask_secrets(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        return mask_secrets(value)

    def get_status_summary(self) -> str:
        """Returns a summary of the resource's status."""
        return f"Resource {self.metadata.name} in {self.metadata.namespace} has status: {self.status}"


# class NamespaceResources(BaseModel):
#     """Represents resources grouped by namespace."""
#     namespace: str = Field(..., description="The namespace of the resources.")
#     resources: Dict[str, List[str]] = Field(..., description="Generalized structure for different resource types.")

#     def get_resource_count(self) -> int:
#         """Returns the total count of resources in the namespace."""
#         return sum(len(resource_list) for resource_list in self.resources.values())


class S3Account(BaseModel):
    access_key: str = Field(..., description="The access key for the S3 account.")
    secret_key: str = Field(..., description="The secret key for the S3 account.")

    def mask_credentials(self) -> Dict[str, str]:
        """Returns the credentials with the secret key masked."""
        return {"access_key": self.access_key, "secret_key": "****"}


class S3AccountRequest(BaseModel):
    access_key: str
    secret_key: str
    endpoint_url: Optional[HttpUrl] = Field(None, description="The endpoint URL for the S3 service.")
    secure_flag: bool = Field(True, description="Flag to indicate if the connection is secure.")
    cert_check: bool = Field(True, description="Flag to indicate if certificate validation is enabled.")



class ConnectionRequest(BaseModel):
    host: str = Field(..., description="The hostname or IP address to connect to.")
    port: int = Field(..., description="The port to connect to.")

    def get_connection_url(self) -> str:
        """Returns the connection URL."""
        return f"{self.host}:{self.port}"


class CRD(BaseModel):
    name: str = Field(..., description="The name of the Custom Resource Definition.")
    group: str = Field(..., description="The API group of the CRD.")
    version: str = Field(..., description="The version of the CRD.")


class CRDItemRequest(BaseModel):
    group: str
    version: str
    plural: str
    namespace: Optional[str] = Field(None, description="The namespace of the CRD item, if applicable.")


class Pod(BaseModel):
    name: str = Field(..., description="The name of the pod.")
    status: str = Field(..., description="The status of the pod.")


class Service(BaseModel):
    name: str = Field(..., description="The name of the service.")
    type: str = Field(..., description="The type of the service.")


class Deployment(BaseModel):
    name: str = Field(..., description="The name of the deployment.")
    replicas: Optional[int] = Field(None, description="The number of replicas for the deployment.")


class NamespaceResources(BaseModel):
    namespace: str = Field(..., description="The namespace of the resources.")
    pods: List[Pod] = Field(..., description="List of pods in the namespace.")
    services: List[Service] = Field(..., description="List of services in the namespace.")
    deployments: List[Deployment] = Field(..., description="List of deployments in the namespace.")

    def get_summary(self) -> Dict[str, int]:
        """Returns a summary of the resources in the namespace."""
        return {
            "pods": len(self.pods),
            "services": len(self.services),
            "deployments": len(self.deployments),
        }

class NotFoundResponse(BaseModel):
    detail: str = Field(..., description="Details about the not found error.")

class KubernetesEvent(BaseModel):
    type: str = Field(..., description="The type of the event.")
    name: str = Field(..., description="The name of the resource associated with the event.")
    namespace: Optional[str] = Field(None, description="The namespace of the resource, if applicable.")
    message: str = Field(..., description="The message associated with the event.")
    reason: Optional[str] = Field(None, description="The reason for the event.")
    timestamp: Optional[datetime] = Field(None, description="The timestamp of the event.")

class StorageClass(BaseModel):
    name: str
    namespace: Optional[str]
    message: str
    reason: Optional[str]
    timestamp: Optional[str]

class DeleteDeploymentRequest(BaseModel):
    namespace: str
    deployment_name: str

class ResourceType(str, Enum):
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    REPLICASET = "replicaset"
    POD = "pod"
    SERVICE = "service"
    PERSISTENTVOLUME = "pv"
    PERSISTENTVOLUMECLAIM = "pvc"
    NAMESPACE = "namespace"

    @classmethod
    def get_resource_types(cls) -> List[str]:
        """Returns a list of all resource types."""
        return [resource_type.value for resource_type in cls]


class DeleteResourceRequest(BaseModel):
    namespace: Optional[str] = Field(..., description="The namespace of the resource.")
    resource_name: str = Field(..., description="The name of the resource to delete.")
    resource_type: ResourceType = Field(..., description="The type of the resource (e.g., deployment, statefulset, replicaset).")
    force: bool = Field(False, description="Flag to indicate if the deletion should be forced.")


class PersistentVolumeClaim(BaseModel):
    name: str
    namespace: str
    status: str
    storage: Optional[str]
    access_modes: Optional[list[str]]
    storage_class: Optional[str]


class PersistentVolume(BaseModel):
    name: str
    status: str
    capacity: Optional[str]
    access_modes: Optional[list[str]]
    reclaim_policy: Optional[str]
    storage_class: Optional[str]
    volume_mode: Optional[str]


class KubeconfigRequest(BaseModel):
    service_account_name: str = Field(..., description="The name of the service account.")
    namespace: str = Field(..., description="The namespace where the service account is located.")

class KubeconfigResponse(BaseModel):
    message: str = Field(..., description="A success message.")
    kubeconfig_path: str = Field(..., description="The path to the generated kubeconfig file.")