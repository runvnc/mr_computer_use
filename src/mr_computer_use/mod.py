from lib.providers.commands import command
import docker
import asyncio
import logging
from .docker_control import check_docker, build_computer_image, ensure_image_available, start_computer_container, stop_computer_container
from .computer_client import get_computer_client

logger = logging.getLogger(__name__)

@command()
async def computer_check_docker(context=None):
    """Check if Docker is installed and running.
    
    Example:
    { "computer_check_docker": {} }
    """
    result = await check_docker(context)
    return result

@command()
async def computer_start(context=None):
    """Start the computer use virtual desktop container.
    If the container doesn't exist, it will be created.
    If the image doesn't exist, it will be pulled from Docker Hub or built.
    
    Example:
    { "computer_start": {} }
    """
    # Check Docker first
    docker_check = await check_docker(context)
    if docker_check["status"] != "ok":
        return docker_check
    
    # Start container
    result = await start_computer_container(context)
    
    # If started successfully, wait a moment and get a screenshot
    if result["status"] == "ok":
        client = await get_computer_client(context)
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
async def computer_stop(context=None):
    """Stop the computer use virtual desktop container.
    
    Example:
    { "computer_stop": {} }
    """
    result = await stop_computer_container(context)
    return result

@command()
async def computer_screenshot(context=None):
    """Get a screenshot from the computer use virtual desktop.
    Similar to examine_image, this will insert the screenshot into the chat.
    
    Example:
    { "computer_screenshot": {} }
    """
    client = await get_computer_client(context)
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
async def computer_click(x, y, context=None):
    """Click at specified coordinates in the computer use virtual desktop.
    
    Parameters:
    x - Integer. The x coordinate to click.
    y - Integer. The y coordinate to click.
    
    Example:
    { "computer_click": {"x": 100, "y": 200} }
    """
    if x is None or y is None:
        return {"status": "error", "message": "Missing x or y coordinates"}
    
    client = await get_computer_client(context)
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
async def computer_type(text, context=None):
    """Type text in the computer use virtual desktop.
    
    Parameters:
    text - String. The text to type.
    
    Example:
    { "computer_type": {"text": "Hello, world!"} }
    """
    if not text:
        return {"status": "error", "message": "Missing text parameter"}
    
    client = await get_computer_client(context)
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
async def computer_press_key(key, context=None):
    """Press a keyboard key in the computer use virtual desktop.
    
    Parameters:
    key - String. The key to press (e.g., "enter", "tab", "escape").
    
    Example:
    { "computer_press_key": {"key": "enter"} }
    """
    if not key:
        return {"status": "error", "message": "Missing key parameter"}
    
    client = await get_computer_client(context)
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
async def computer_navigate(url, context=None):
    """Navigate to a URL in the browser in the computer use virtual desktop.
    
    Parameters:
    url - String. The URL to navigate to.
    
    Example:
    { "computer_navigate": {"url": "https://www.example.com"} }
    """
    if not url:
        return {"status": "error", "message": "Missing url parameter"}
    
    client = await get_computer_client(context)
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
@command()
async def computer_scroll(amount, axis='v', context=None):
    """Scroll the page vertically or horizontally.
    
    Parameters:
    amount - Integer. Positive for down/right, negative for up/left scrolling.
    axis - String. 'v' for vertical (default), 'h' for horizontal scrolling.
    
    Example:
    { "computer_scroll": {"amount": 300} }  # Scroll down 300 pixels
    { "computer_scroll": {"amount": -100, "axis": "h"} }  # Scroll left 100 pixels
    """
    client = await get_computer_client(context)
    result = await client.scroll(amount, axis)
    
    # Get a screenshot after scrolling to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-scroll screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def computer_mouse_move(x, y, context=None):
    """Move the mouse cursor to the specified coordinates without clicking.
    
    Parameters:
    x - Integer. The x coordinate to move to.
    y - Integer. The y coordinate to move to.
    
    Example:
    { "computer_mouse_move": {"x": 100, "y": 200} }
    """
    client = await get_computer_client(context)
    result = await client.mouse_move(x, y)
    return result

@command()
async def computer_right_click(context=None):
    """Perform a right mouse click at the current cursor position.
    Use computer_mouse_move first to position the cursor.
    
    Example:
    { "computer_right_click": {} }
    """
    client = await get_computer_client(context)
    result = await client.right_click()
    
    # Get a screenshot after clicking to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-right-click screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def computer_double_click(context=None):
    """Perform a double-click at the current cursor position.
    Use computer_mouse_move first to position the cursor.
    
    Example:
    { "computer_double_click": {} }
    """
    client = await get_computer_client(context)
    result = await client.double_click()
    
    # Get a screenshot after clicking to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-double-click screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def computer_drag(start_x, start_y, end_x, end_y, hold_ms=100, context=None):
    """Perform a drag operation from start to end coordinates.
    
    Parameters:
    start_x - Integer. The starting x coordinate.
    start_y - Integer. The starting y coordinate.
    end_x - Integer. The ending x coordinate.
    end_y - Integer. The ending y coordinate.
    hold_ms - Integer. Optional. Hold time in milliseconds (default: 100).
    
    Example:
    { "computer_drag": {"start_x": 100, "start_y": 200, "end_x": 300, "end_y": 400} }
    """
    client = await get_computer_client(context)
    result = await client.drag(start_x, start_y, end_x, end_y, hold_ms)
    
    # Get a screenshot after dragging to show the result
    try:
        screenshot = await client.get_screenshot()
        if screenshot:
            await context.format_image_message(screenshot)
    except Exception as e:
        logger.error(f"Post-drag screenshot error: {str(e)}")
        pass  # Don't fail the command if screenshot fails
    
    return result

@command()
async def computer_get_cursor_position(context=None):
    """Get the current cursor position.
    
    Example:
    { "computer_get_cursor_position": {} }
    """
    client = await get_computer_client(context)
    return await client.get_cursor_position()
