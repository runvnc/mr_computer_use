from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from lib.templates import render
from .docker_control import check_docker, start_computer_container, stop_computer_container
import docker
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/computer_use")
async def computer_use_page(request: Request):
    """Main computer use viewer page"""
    user = request.state.user.username if hasattr(request.state, 'user') else None
    html = await render('computer_use_view', {"user": user})
    return HTMLResponse(html)

@router.get("/computer_use/api/status")
async def computer_use_status(request: Request):
    """Get computer use container status"""
    docker_check = await check_docker()
    if docker_check["status"] != "ok":
        return JSONResponse({"status": "docker_error", "message": docker_check["message"]})
    
    # Check if container is running
    try:
        client = docker.from_env()
        containers = client.containers.list(filters={"name": "mindroot_computer_use"})
        if containers:
            return JSONResponse({"status": "running"})
        
        # Check if container exists but is stopped
        containers = client.containers.list(all=True, filters={"name": "mindroot_computer_use"})
        if containers:
            return JSONResponse({"status": "stopped"})
        
        return JSONResponse({"status": "not_created"})
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@router.post("/computer_use/api/start")
async def computer_use_start(request: Request):
    """Start computer use container"""
    result = await start_computer_container()
    return JSONResponse(result)

@router.post("/computer_use/api/stop")
async def computer_use_stop(request: Request):
    """Stop computer use container"""
    result = await stop_computer_container()
    return JSONResponse(result)
