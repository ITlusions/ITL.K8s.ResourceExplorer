# **Authentication Module Documentation**

The auth.py module provides functionality for API key-based authentication in a Kubernetes environment. It retrieves and validates API keys from Kubernetes secrets, environment variables, or generates fallback keys for local testing.

---

## **Class: `AuthWrapper`**

### **Overview**
The `AuthWrapper` class is responsible for managing API key authentication. It supports retrieving API keys from Kubernetes secrets, environment variables, or generating fallback keys for local development.

---

### **Initialization**

#### **Constructor: `__init__`**
```python
def __init__(self, k8s_helper=None, enable_validation: bool = True)
```

- **Args**:
  - `k8s_helper`: An instance of `KubernetesHelper` (optional, for dependency injection).
  - `enable_validation`: A boolean flag to enable or disable API key validation (useful for local development).

- **Attributes**:
  - `API_KEY_NAME`: The name of the HTTP header used for API key authentication (`X-API-Key`).
  - `api_key_header`: FastAPI's `APIKeyHeader` dependency for extracting the API key from request headers.
  - `k8s_helper`: An instance of `KubernetesHelper` for interacting with Kubernetes runtime context.
  - `enable_validation`: Whether API key validation is enabled.
  - `API_KEY`: The API key retrieved from Kubernetes secrets, environment variables, or generated as a fallback.

---

### **Methods**

#### **1. `_initialize_api_key`**
```python
def _initialize_api_key() -> str
```

- **Description**:
  Initializes the API key by:
  1. Retrieving it from a Kubernetes secret.
  2. Falling back to an environment variable (`FALLBACK_API_KEY`).
  3. Generating a fallback key for local testing.

- **Returns**:
  - The API key as a string.

- **Logs**:
  - Logs the source of the API key (Kubernetes secret, environment variable, or fallback).

---

#### **2. `_generate_fallback_key`**
```python
def _generate_fallback_key() -> str
```

- **Description**:
  Generates a fallback API key for local testing. The key is a base64-encoded string containing:
  - A prefix (`resource-explorer:fallback_key`).
  - A timestamp.
  - A randomly generated UUID.

- **Returns**:
  - The base64-encoded fallback API key.

- **Example**:
  - Before encoding: `resource-explorer:fallback_key:1695379200:123e4567-e89b-12d3-a456-426614174000`
  - After encoding: `cmVzb3VyY2UtZXhwbG9yZXI6ZmFsbGJhY2tfa2V5OjE2OTUzNzkyMDA6MTIzZTQ1NjctZTg5Yi0xMmQzLWE0NTYtNDI2NjE0MTc0MDAw`

---

#### **3. `get_api_key_from_k8s_secret`**
```python
def get_api_key_from_k8s_secret(secret_name: str, namespace: str, key: str) -> str
```

- **Description**:
  Retrieves the API key from a Kubernetes secret and decodes it from base64.

- **Args**:
  - `secret_name`: The name of the Kubernetes secret.
  - `namespace`: The namespace where the secret is located.
  - `key`: The key in the secret containing the API key.

- **Returns**:
  - The decoded API key as a string.

- **Raises**:
  - `RuntimeError`: If the secret or key is not found, or if decoding fails.

- **Logs**:
  - Logs the encoded and decoded API key for debugging purposes.

---

#### **4. `validate_api_key`**
```python
def validate_api_key(api_key: str = Depends(APIKeyHeader(name="X-API-Key")))
```

- **Description**:
  Validates the provided API key against the one retrieved from the Kubernetes secret.

- **Args**:
  - `api_key`: The API key provided in the request header.

- **Returns**:
  - The validated API key.

- **Raises**:
  - `HTTPException`: If the API key is invalid.

- **Logs**:
  - Logs whether the API key validation succeeded or failed.

---

### **Environment Variables**

The following environment variables are used by the `AuthWrapper` class:

1. **`API_SECRET_NAME`**:
   - Default: `re-api-key`
   - The name of the Kubernetes secret containing the API key.

2. **`API_SECRET_KEY`**:
   - Default: `api-key`
   - The key in the Kubernetes secret containing the API key.

3. **`FALLBACK_API_KEY`**:
   - Optional.
   - A fallback API key for local testing.

---

### **Kubernetes Secret Example**

To use the `AuthWrapper` class with a Kubernetes secret, create the secret as follows:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: re-api-key
  namespace: ivz-resource-explorer
type: Opaque
data:
  api-key: bXktc2VjcmV0LWFwaS1rZXk=  # Base64-encoded value of "my-secret-api-key"
```

---

### **Usage Example**

#### **FastAPI Integration**
```python
from fastapi import FastAPI, Depends
from base.auth import AuthWrapper

app = FastAPI()
auth_wrapper = AuthWrapper()

@app.get("/secure-endpoint")
def secure_endpoint(api_key: str = Depends(auth_wrapper.validate_api_key)):
    return {"message": "You have access to this secure endpoint!"}
```

#### **Request Example**
```bash
curl -H "X-API-Key: my-secret-api-key" http://localhost:8000/secure-endpoint
```

---

### **Logging**

The `AuthWrapper` class uses Python's `logging` module to log important events, such as:
- Successful or failed retrieval of the API key.
- Validation success or failure.
- Fallback to environment variables or generated keys.

---

### **Error Handling**

1. **Invalid API Key**:
   - Returns a `403 Forbidden` response with the message `"Invalid API Key"`.

2. **Missing Kubernetes Secret**:
   - Logs a warning and falls back to the environment variable or generates a fallback key.

---

### **Best Practices**

- Use Kubernetes secrets for storing API keys in production environments.
- Use the fallback key only for local testing or development.
- Ensure proper RBAC permissions for the service account to access Kubernetes secrets.