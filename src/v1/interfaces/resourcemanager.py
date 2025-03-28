from abc import ABC, abstractmethod

class TestManagerInterface(ABC):
    @abstractmethod
    async def test_smtp(self, host: str):
        """
        Test SMTP
        """
        pass

    @abstractmethod
    async def test_dns(self, hostr: str):
        """
        Test DNS
        """
        pass