from lib.providers.services import service
import docker
import os
import logging
import json

logger = logging.getLogger(__name__)

# Configuration with defaults
DEFAULT_CONFIG = {
    "docker_image": "runvnc/bytebot:latest",  # Pre-built Docker Hub image
    "container_name": "mindroot_computer_use",
    "ports": {
        "8080/tcp": 8080,  # Bytebot API
        "5900/tcp": 5900,  # VNC
        "6080/tcp": 6080   # noVNC
    },
    "build_if_not_found": True,  # Whether to attempt building if image not found
    "repo_url": "https://github.com/bytebot-ai/bytebot.git"
}

def _get_config():
    """Get configuration, with user overrides if available"""
    config = DEFAULT_CONFIG.copy()
    
    # Check for config file
    config_path = os.path.expanduser("~/.mindroot/computer_use_config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                config.update(user_config)
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
    
    return config

class DockerException(Exception):
    pass

@service()
async def check_docker(context=None):
    """Check if Docker is installed and running"""
    try:
        client = docker.from_env()
        return {"status": "ok", "version": client.version()}
    except Exception as e:
        logger.error(f"Docker check failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@service()
async def build_bytebot_image(context=None):
    """Build the bytebot Docker image"""
    config = _get_config()
    try:
        client = docker.from_env()
        # Clone the repo if not already present
        repo_path = "/tmp/bytebot"
        if not os.path.exists(repo_path):
            os.system(f"git clone {config['repo_url']} {repo_path}")
        
        # Build the image
        image, logs = client.images.build(
            path=repo_path,
            tag=config['docker_image'],
            rm=True
        )
        return {"status": "ok", "image_id": image.id}
    except Exception as e:
        logger.error(f"Build failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@service()
async def ensure_image_available(context=None):
    """Ensure the Docker image is available, pulling or building if necessary"""
    config = _get_config()
    try:
        client = docker.from_env()
        try:
            # Try to get the image
            image = client.images.get(config['docker_image'])
            return {"status": "ok", "image_id": image.id, "source": "local"}
        except docker.errors.ImageNotFound:
            # Try to pull the image from Docker Hub
            try:
                image = client.images.pull(config['docker_image'])
                return {"status": "ok", "image_id": image.id, "source": "pulled"}
            except Exception as pull_error:
                if config['build_if_not_found']:
                    # Try to build the image
                    logger.info(f"Failed to pull image, attempting to build: {str(pull_error)}")
                    build_result = await build_bytebot_image(context)
                    if build_result["status"] == "ok":
                        build_result["source"] = "built"
                        return build_result
                    else:
                        logger.error(f"Failed to build image: {build_result}")
                        return build_result
                else:
                    raise Exception(f"Image not found and build_if_not_found is disabled: {str(pull_error)}")
    except Exception as e:
        logger.error(f"Failed to ensure image availability: {str(e)}")
        return {"status": "error", "message": str(e)}

@service()
async def start_bytebot_container(context=None):
    """Start a bytebot container"""
    config = _get_config()
    try:
        client = docker.from_env()
        # Check if container already exists
        existing = client.containers.list(all=True, filters={"name": config['container_name']})
        
        if existing:
            container = existing[0]
            if container.status != "running":
                container.start()
        else:
            # Ensure image is available
            image_result = await ensure_image_available(context)
            if image_result["status"] != "ok":
                return image_result
            
            # Create and start new container
            container = client.containers.run(
                config['docker_image'],
                name=config['container_name'],
                ports=config['ports'],
                detach=True
            )
            
        ports = {}
        for container_port, host_port in config['ports'].items():
            ports[container_port.split('/')[0]] = host_port
            
        return {
            "status": "ok", 
            "container_id": container.id,
            "ports": ports
        }
    except Exception as e:
        logger.error(f"Container start failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@service()
async def stop_bytebot_container(context=None):
    """Stop the bytebot container"""
    config = _get_config()
    try:
        client = docker.from_env()
        containers = client.containers.list(filters={"name": config['container_name']})
        
        if containers:
            container = containers[0]
            container.stop()
            return {"status": "ok"}
        return {"status": "not_found"}
    except Exception as e:
        logger.error(f"Container stop failed: {str(e)}")
        return {"status": "error", "message": str(e)}
