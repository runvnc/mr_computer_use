from lib.providers.commands import command
import docker
import asyncio
import logging
from .docker_utils import check_docker, build_bytebot_image, ensure_image_available, start_bytebot_container, stop_bytebot_container
from .bytebot_client import get_bytebot_client

logger = logging.getLogger(__name__)

@command()
async def bytebot_check_docker(params, context=None):
    """Check if Docker is installed and running.
    
    Example:
    { "bytebot_check_docker": {} }
    """
    result = await check_docker(context)
    return result

@command()
async def bytebot_start(params, context=None):
    """Start the computer use virtual desktop container.
    If the container doesn't exist, it will be created.
    If the image doesn't exist, it will be pulled from Docker Hub or built.
    
    Example:
    { "bytebot_start": {} }
    """
    # Check Docker first
    docker_check = await check_docker(context)
    if docker_check["status"] != "ok":
        return docker_check
    
    # Start container
    result = await start_bytebot_container(context)
    
    # If started successfully, wait a moment and get a screenshot
    if result["status"] == "ok":
        client = await get_bytebot_client(context)
        try:
            # Wait a moment for the desktop to initialize
            await asyncio.sleep(5)  
            
            screenshot = await client.get_screenshot()
            if screenshot:
                # Insert the screenshot into the chat
                image_message = await context.format_image_message(screenshot)
                result["screenshot"] = "added to chat"
                result["image_message"] = image_message
            else:
                result["screenshot"] = "failed to capture"
        except Exception as e:
            logger.error(f"Screenshot error: {str(e)}")
            result["screenshot_error"] = str(e)
    
    return result

@command()
async def bytebot_stop(params, context=None):
    """Stop the computer use virtual desktop container.
    
    Example:
    { "bytebot_stop": {} }
    """
    result = await stop_bytebot_container(context)
    return result

@command()
async def bytebot_screenshot(params, context=None):
    """Get a screenshot from the computer use virtual desktop.
    Similar to examine_image, this will insert the screenshot into the chat.
    
    Example:
    { "bytebot_screenshot": {} }
    """
    client = await get_bytebot_client(context)
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            # Insert the screenshot into the chat context
            message = await context.format_image_message(screenshot)
            return message
        else:
            return {"status": "error", "message": "Failed to get screenshot"}
    except Exception as e:
        logger.error(f"Screenshot command error: {str(e)}")
        return {"status": "error", "message": str(e)}

@command()
async def bytebot_click(params, context=None):
    """Click at specified coordinates in the computer use virtual desktop.
    
    Parameters:
    x - Integer. The x coordinate to click.
    y - Integer. The y coordinate to click.
    
    Example:
    { "bytebot_click": {"x": 100, "y": 200} }
    """
    x = params.get("x")
    y = params.get("y")
    
    if x is None or y is None:
        return {"status": "error", "message": "Missing x or y coordinates"}
    
    client = await get_bytebot_client(context)
    result = await client.click(x, y)
    
    # Get a screenshot after clicking to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-click screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def bytebot_type(params, context=None):
    """Type text in the computer use virtual desktop.
    
    Parameters:
    text - String. The text to type.
    
    Example:
    { "bytebot_type": {"text": "Hello, world!"} }
    """
    text = params.get("text")
    
    if not text:
        return {"status": "error", "message": "Missing text parameter"}
    
    client = await get_bytebot_client(context)
    result = await client.type_text(text)
    
    # Get a screenshot after typing to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-type screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def bytebot_press_key(params, context=None):
    """Press a keyboard key in the computer use virtual desktop.
    
    Parameters:
    key - String. The key to press (e.g., "enter", "tab", "escape").
    
    Example:
    { "bytebot_press_key": {"key": "enter"} }
    """
    key = params.get("key")
    
    if not key:
        return {"status": "error", "message": "Missing key parameter"}
    
    client = await get_bytebot_client(context)
    result = await client.press_key(key)
    
    # Get a screenshot after pressing key to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-key screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def bytebot_navigate(params, context=None):
    """Navigate to a URL in the browser in the computer use virtual desktop.
    
    Parameters:
    url - String. The URL to navigate to.
    
    Example:
    { "bytebot_navigate": {"url": "https://www.example.com"} }
    """
    url = params.get("url")
    
    if not url:
        return {"status": "error", "message": "Missing url parameter"}
    
    client = await get_bytebot_client(context)
    result = await client.navigate_to(url)
    
    # Get a screenshot after navigation to show the result
    try:
        # Wait for page to load
        await asyncio.sleep(3)  
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-navigate screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result
