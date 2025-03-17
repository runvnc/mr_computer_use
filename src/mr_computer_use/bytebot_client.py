from lib.providers.services import service
import aiohttp
import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class BytebotClient:
    def __init__(self, api_url="http://localhost:8080"):
        self.api_url = api_url
        
    async def get_screenshot(self):
        """Capture a screenshot from the VM"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/api/screenshot"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        img_data = base64.b64decode(data['screenshot'])
                        img = Image.open(BytesIO(img_data))
                        return img
                    else:
                        logger.error(f"Failed to get screenshot: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            return None
    
    async def click(self, x, y):
        """Click at the specified coordinates"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/api/click"
                payload = {"x": x, "y": y}
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Click error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def type_text(self, text):
        """Type text"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/api/type"
                payload = {"text": text}
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Type text error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def press_key(self, key):
        """Press a keyboard key"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/api/keypress"
                payload = {"key": key}
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Press key error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def navigate_to(self, url):
        """Navigate to a URL in the browser"""
        # This may involve multiple steps like clicking browser, typing URL, etc.
        # For simplicity, assuming an API endpoint exists
        try:
            async with aiohttp.ClientSession() as session:
                api_url = f"{self.api_url}/api/navigate"
                payload = {"url": url}
                async with session.post(api_url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Navigate error: {str(e)}")
            return {"status": "error", "message": str(e)}

@service()
async def get_bytebot_client(context=None):
    """Get a configured bytebot client instance"""
    return BytebotClient()
