import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import HTTPException

def test_s3_account(access_key: str, secret_key: str, endpoint_url: str = None, secure_flag: bool = True, cert_check: bool = True) -> dict:
    """
    Tests an S3-compatible account by validating the provided credentials using boto3.
    
    Args:
        access_key (str): The access key for the S3-compatible storage.
        secret_key (str): The secret key for the S3-compatible storage.
        endpoint_url (str, optional): The custom endpoint URL for S3-compatible storage (e.g., MinIO).
        secure_flag (bool): Whether to use HTTPS (True) or HTTP (False).
        cert_check (bool): Whether to verify SSL certificates (True) or disable verification (False).
    
    Returns:
        dict: A dictionary containing the status and message of the validation.
    """
    if not access_key or not secret_key:
        raise HTTPException(status_code=400, detail="Access key and secret key are required.")

    try:
        # Create an S3 client with the provided credentials and optional endpoint URL
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            use_ssl=secure_flag,  # Enable/disable HTTPS
            verify=cert_check,   # Enable/disable SSL certificate verification
        )

        # Attempt to list buckets to validate credentials
        s3_client.list_buckets()

        return {"status": "success", "message": "S3 account validated successfully."}

    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid S3 credentials.")
    except PartialCredentialsError:
        raise HTTPException(status_code=400, detail="Incomplete S3 credentials provided.")
    except ClientError as e:
        raise HTTPException(status_code=403, detail=f"S3 Client Error: {e.response['Error']['Message']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")