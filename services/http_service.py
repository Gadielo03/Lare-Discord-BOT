"""HTTP Service - Manages persistent aiohttp session"""
import aiohttp
from utils.logger import log


class HttpService:
    """Service for managing a single persistent HTTP session"""
    
    _instance = None
    _session = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance"""
        if cls._instance is None:
            cls._instance = super(HttpService, cls).__new__(cls)
        return cls._instance
    
    async def get_session(self):
        """Get or create the HTTP session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
            log.debug("Created new HTTP session")
        return self._session
    
    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
            log.debug("Closed HTTP session")
    
    async def get(self, url, params=None, **kwargs):
        """Make a GET request using the persistent session"""
        session = await self.get_session()
        try:
            async with session.get(url, params=params, **kwargs) as response:
                return response
        except Exception as e:
            log.error(f"HTTP GET error: {e}")
            raise
