"""Kubernetes tools — @tool wrappers around kubectl commands."""
import subprocess
from typing import Any, Dict

from strands import tool


@tool
def kubectl_apply(manifest_path: str, namespace: str = "default") -> Dict[str, Any]:
    """Apply a Kubernetes manifest file.

    Args:
        manifest_path: Path to the YAML manifest file to apply.
        namespace: Kubernetes namespace (default: default).
    """
    result = subprocess.run(
        ["kubectl", "apply", "-f", manifest_path, "-n", namespace],
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
def kubectl_get_pods(namespace: str = "default") -> Dict[str, Any]:
    """Get the list of pods in a namespace.

    Args:
        namespace: Kubernetes namespace to query (default: default).
    """
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "wide"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


@tool
def kubectl_logs(pod_name: str, namespace: str = "default", tail_lines: int = 50) -> Dict[str, Any]:
    """Fetch logs from a Kubernetes pod.

    Args:
        pod_name: Name of the pod.
        namespace: Kubernetes namespace (default: default).
        tail_lines: Number of lines to retrieve from the end of the log (default: 50).
    """
    result = subprocess.run(
        ["kubectl", "logs", pod_name, "-n", namespace, f"--tail={tail_lines}"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }


@tool
def kubectl_delete(resource_type: str, resource_name: str, namespace: str = "default") -> Dict[str, Any]:
    """Delete a Kubernetes resource.

    Args:
        resource_type: Type of resource (e.g. pod, deployment, service).
        resource_name: Name of the resource to delete.
        namespace: Kubernetes namespace (default: default).
    """
    result = subprocess.run(
        ["kubectl", "delete", resource_type, resource_name, "-n", namespace],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }
