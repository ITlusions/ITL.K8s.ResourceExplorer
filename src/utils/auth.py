from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
import os

# OAuth2PasswordBearer expects the token to be passed as a Bearer token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Load environment variables
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
PUBLIC_KEY_URL = f"{AUTHORITY}/discovery/v2.0/keys"

# Define the token validation function
def validate_token(token: str = Depends(oauth2_scheme)):
    """
    Validate the provided JWT token issued by Entra ID.
    """
    try:
        # Decode the token without verifying the signature (to extract header)
        unverified_header = jwt.get_unverified_header(token)

        # Fetch the public keys from Entra ID
        from urllib.request import urlopen
        import json

        with urlopen(PUBLIC_KEY_URL) as response:
            jwks = json.load(response)

        # Find the key that matches the token's "kid" (key ID)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not find a matching public key.",
            )

        # Decode and verify the token using the public key
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=CLIENT_ID,
            issuer=f"{AUTHORITY}/v2.0",
        )

        # Extract user information from the token
        username = payload.get("preferred_username")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain a valid username.",
            )

        return payload  # Return the decoded token payload (user info)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )