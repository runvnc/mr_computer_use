from lib.providers.services import service
import aiohttp
import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ComputerClient:
    def __init__(self, api_url="http://localhost:3100"):
        self.api_url = api_url
        
    async def get_screenshot(self):
        """Capture a screenshot from the VM"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/screenshot"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        img_data = base64.b64decode(data['image'].split(',')[1] if ',' in data['image'] else data['image'])
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
                # First move to the coordinates
                url = f"{self.api_url}/computer-use/mouse-move"
                payload = {"x": x, "y": y}
                await session.post(url, json=payload)
                
                # Then click
                url = f"{self.api_url}/computer-use/left-click"
                async with session.post(url) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Click error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def type_text(self, text):
        """Type text"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/type"
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
                url = f"{self.api_url}/computer-use/key"
                payload = {"key": key}
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Press key error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def navigate_to(self, url):
        """Navigate to a URL in the browser"""
        # This requires multiple steps as there's no direct API
        try:
            # Start Firefox (assuming it's in the dock or desktop)
            await self.click(100, 100)  # Click somewhere in the desktop
            await self.press_key("alt-F2")  # Open run dialog
            await self.type_text("firefox")  # Type firefox
            await self.press_key("Return")  # Press enter
            
            # Wait for browser to open
            import asyncio
            await asyncio.sleep(3)
            
            # Type the URL and navigate
            await self.press_key("ctrl-l")  # Focus address bar
            await self.type_text(url)  # Type the URL
            await self.press_key("Return")  # Press enter
            
            return {"status": "ok", "message": f"Navigated to {url}"}
        except Exception as e:
            logger.error(f"Navigate error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def scroll(self, amount, axis='v'):
        """Scroll vertically or horizontally
        
        Args:
            amount: Integer. Positive for down/right, negative for up/left
            axis: String. 'v' for vertical, 'h' for horizontal
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/scroll"
                payload = {"amount": amount, "axis": axis}
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Scroll error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def mouse_move(self, x, y):
        """Move the mouse cursor to the specified coordinates"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/mouse-move"
                payload = {"x": x, "y": y}
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Mouse move error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def right_click(self):
        """Perform a right mouse click at the current cursor position"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/right-click"
                async with session.post(url) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Right click error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def double_click(self):
        """Perform a double-click at the current cursor position"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/double-click"
                async with session.post(url) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Double click error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def drag(self, start_x, start_y, end_x, end_y, hold_ms=100):
        """Perform a drag operation from start to end coordinates"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/left-click-drag"
                payload = {
                    "startX": start_x,
                    "startY": start_y,
                    "endX": end_x,
                    "endY": end_y,
                    "holdMs": hold_ms
                }
                async with session.post(url, json=payload) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Drag error: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_cursor_position(self):
        """Get the current cursor position"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_url}/computer-use/cursor-position"
                async with session.get(url) as response:
                    return await response.json()
        except Exception as e:
            logger.error(f"Get cursor position error: {str(e)}")
            return {"status": "error", "message": str(e)}

@service()
async def get_computer_client(context=None):
    """Get a configured computer client instance"""
    return ComputerClient()
