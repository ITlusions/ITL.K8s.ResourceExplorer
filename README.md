# ITlusions Kubernetes Resource Explorer Service

## Overview

The ITlusions Kubernetes Resource Explorer Service is a FastAPI-based application designed to interact with Kubernetes clusters. It provides endpoints to list namespaces, secrets, and describe various Kubernetes resources such as pods, services, and deployments. This service is intended to help explore and manage their Kubernetes resources efficiently.

## Features

- **List Namespaces**: Retrieve a list of all namespaces in the Kubernetes cluster.
- **List Secrets**: Retrieve a list of all secrets in the Kubernetes cluster.
- **Describe Resources**: Get detailed information about specific Kubernetes resources (pods, services, deployments).

## Architecture

The service is built using FastAPI and interacts with the Kubernetes API using the official Kubernetes Python client. It is containerized using Docker and can be deployed using Docker Compose or Helm.

## Prerequisites

- Docker
- Docker Compose (for local testing)
- Kubernetes cluster (using Helm)
- kubectl configured to access the cluster

## Installation

### Using Docker Compose

1. Clone the repository:

    ```sh
    git clone https://github.com/itlusions/itl-k8s-re.git
    cd itl-k8s-re
    ```

2. Ensure your Kubernetes configuration is set correctly .

3. Build and start the service:

    ```sh
    docker-compose up --build
    ```

4. Access the service at `http://localhost:8000`.

### Using Helm

## Configuration

### Environment Variables

- `KUBECONFIG`: Path to the Kubernetes configuration file.

### Docker Compose

The `docker-compose.yml` file mounts the Kubernetes configuration and sets the necessary environment variables.

### Helm

The `values.yaml` file contains configuration options for the Helm chart, including image settings, service account, ingress, and resource limits.

## Usage

### Endpoints

- **Health Check**: `GET /health`
- **Readiness Check**: `GET /readiness`
- **List Namespaces**: `GET /v1/get-namespaces`
- **List Secrets**: `GET /v1/get-secrets`
- **Describe Resource**: `GET /v1/describe/{namespace}/{resource_type}/{resource_name}`

### Example Requests

1. **List Namespaces**:

    ```sh
    curl http://localhost:8000/v1/get-namespaces
    ```

2. **List Secrets**:

    ```sh
    curl http://localhost:8000/v1/get-secrets
    ```

3. **Describe a Pod**:

    ```sh
    curl http://localhost:8000/v1/describe/default/pod/my-pod
    ```

## Development

### Requirements

- Python 3.12
- pip

### Setup

1. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

2. Run the application:

    ```sh
    uvicorn main:app --reload
    ```

## Testing

None