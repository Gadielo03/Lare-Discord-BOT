"""GIF Service - Manages GIF retrieval from Tenor API"""
import random
import os
import aiohttp
from utils.logger import log


class GifService:
    """Service for fetching GIFs from Tenor API"""
    
    TENOR_API_KEY = os.getenv("TENOR_API_KEY", "AIzaSyAyimkuYQYF_FXVALexPuGQctUWRURdCYQ")  # Demo key
    TENOR_BASE_URL = "https://tenor.googleapis.com/v2"
    
    async def get_random_gif(self, category: str):
        try:
            gif_url = await self._fetch_from_tenor(category)
            if gif_url:
                log.debug(f"Fetched {category} GIF from Tenor API")
                return gif_url
            else:
                log.warning(f"No GIF found for category '{category}'")
                return None
        except Exception as e:
            log.error(f"Error fetching GIF: {e}")
            return None
    
    async def _fetch_from_tenor(self, category: str, limit: int = 20):
        try:
            search_term = f"anime {category}"
            url = f"{self.TENOR_BASE_URL}/search"
            params = {
                "q": search_term,
                "key": self.TENOR_API_KEY,
                "limit": limit,
                "media_filter": "gif",
                "contentfilter": "high"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("results"):
                            result = random.choice(data["results"])
                            return result["media_formats"]["gif"]["url"]
            
            return None
        except Exception as e:
            log.error(f"Error fetching from Tenor API: {e}")
            return None
