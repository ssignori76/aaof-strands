"""Shell tools — generic subprocess @tool for running shell commands."""
import subprocess
from typing import Any, Dict

from strands import tool


@tool
def run_command(command: str, timeout: int = 60, working_dir: str = ".") -> Dict[str, Any]:
    """Run a shell command and return its output.

    This tool executes arbitrary shell commands via subprocess.  It captures
    both stdout and stderr and returns them along with the exit code.

    Args:
        command: The shell command to run (passed to bash -c).
        timeout: Maximum seconds to wait before killing the process (default: 60).
        working_dir: Working directory for the command (default: current dir).
    """
    try:
        result = subprocess.run(
            command,
            shell=True,  # noqa: S602 — intentional, user-controlled orchestrator
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=working_dir,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "success": False,
        }
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
            "success": False,
        }
