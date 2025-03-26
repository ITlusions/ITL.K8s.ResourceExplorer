import socket
from fastapi import HTTPException

def test_connection(host: str, port: int) -> dict:
    """
    Tests the connection to a host and port. Resolves the hostname to an IP if necessary.
    
    Args:
        host (str): The hostname or IP address to connect to.
        port (int): The port to connect to.
    
    Returns:
        dict: A dictionary containing the resolved IP and connection status.
    """
    try:
        # Resolve hostname to IP address if necessary
        resolved_ip = socket.gethostbyname(host)
    except socket.gaierror:
        raise HTTPException(status_code=400, detail=f"Unable to resolve host: {host}")

    # Attempt to connect to the host and port
    try:
        with socket.create_connection((resolved_ip, port), timeout=5):
            connection_status = "success"
    except (socket.timeout, ConnectionRefusedError) as e:
        connection_status = f"failed: {str(e)}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    return {
        "resolved_ip": resolved_ip,
        "connection_status": connection_status,
    }