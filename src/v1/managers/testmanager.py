import smtplib
import socket
from v1.interfaces.resourcemanager import TestManagerInterface

class TestManager(TestManagerInterface):
    async def test_smtp(self, host: str, use_starttls: bool = False):
        """
        Test SMTP by attempting to connect to the SMTP server.
        Optionally use STARTTLS if requested.
        """
        try:
            server = smtplib.SMTP(host, 25, timeout=5)
            if use_starttls:
                server.starttls()
            server.noop()  # Send a NOOP command to test the connection
            server.quit()
            return {
                "status": "success",
                "message": f"Successfully connected to SMTP server at {host}{' with STARTTLS' if use_starttls else ''}"
            }
        except Exception as e:
            return {
                "status": "failure",
                "message": f"Failed to connect to SMTP server at {host}{' with STARTTLS' if use_starttls else ''}: {str(e)}"
            }

    async def test_dns(self, host: str):
        """
        Test DNS by resolving the hostname to an IP address.
        """
        try:
            ip_address = socket.gethostbyname(host)
            return {"status": "success", "message": f"DNS resolution successful for {host}: {ip_address}"}
        except Exception as e:
            return {"status": "failure", "message": f"DNS resolution failed for {host}: {str(e)}"}