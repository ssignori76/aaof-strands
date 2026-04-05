"""Docker tools — @tool wrappers around docker and docker compose commands."""
import subprocess
from typing import Any, Dict

from strands import tool


@tool
def docker_build(context_path: str, image_tag: str, dockerfile: str = "Dockerfile") -> Dict[str, Any]:
    """Build a Docker image from a Dockerfile.

    Args:
        context_path: Path to the Docker build context directory.
        image_tag: Tag to assign to the built image (e.g. myapp:latest).
        dockerfile: Name of the Dockerfile (default: Dockerfile).
    """
    result = subprocess.run(
        ["docker", "build", "-t", image_tag, "-f", dockerfile, context_path],
        capture_output=True,
        text=True,
        timeout=300,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


@tool
def docker_compose_up(compose_file: str = "docker-compose.yml", detach: bool = True) -> Dict[str, Any]:
    """Start services defined in a docker-compose file.

    Args:
        compose_file: Path to the docker-compose.yml file.
        detach: If True, run containers in the background (default: True).
    """
    cmd = ["docker", "compose", "-f", compose_file, "up"]
    if detach:
        cmd.append("-d")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


@tool
def docker_compose_down(compose_file: str = "docker-compose.yml", remove_volumes: bool = False) -> Dict[str, Any]:
    """Stop and remove services defined in a docker-compose file.

    Args:
        compose_file: Path to the docker-compose.yml file.
        remove_volumes: If True, also remove named volumes (default: False).
    """
    cmd = ["docker", "compose", "-f", compose_file, "down"]
    if remove_volumes:
        cmd.append("-v")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


@tool
def docker_health_check(container_name: str) -> Dict[str, Any]:
    """Check the health status of a running Docker container.

    Args:
        container_name: Name or ID of the container to inspect.
    """
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
        capture_output=True,
        text=True,
        timeout=15,
    )
    status = result.stdout.strip()
    return {
        "returncode": result.returncode,
        "status": status,
        "healthy": status == "healthy",
        "stderr": result.stderr,
    }
