import smtplib
import socket
from v1.interfaces.resourcemanager import TestManagerInterface

class TestManager(TestManagerInterface):
    async def test_smtp(self, host: str):
        """
        Test SMTP by attempting to connect to the SMTP server.
        """
        try:
            server = smtplib.SMTP(host, 25, timeout=5)
            server.noop()  # Send a NOOP command to test the connection
            server.quit()
            return {"status": "success", "message": f"Successfully connected to SMTP server at {host}"}
        except Exception as e:
            return {"status": "failure", "message": f"Failed to connect to SMTP server at {host}: {str(e)}"}

    async def test_dns(self, host: str):
        """
        Test DNS by resolving the hostname to an IP address.
        """
        try:
            ip_address = socket.gethostbyname(host)
            return {"status": "success", "message": f"DNS resolution successful for {host}: {ip_address}"}
        except Exception as e:
            return {"status": "failure", "message": f"DNS resolution failed for {host}: {str(e)}"}