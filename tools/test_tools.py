"""Test tools — @tool functions for running tests and smoke tests."""
import os
import subprocess
from pathlib import Path
from typing import Any, Dict

import requests

from strands import tool


@tool
def smoke_test(url: str = "http://localhost:3000/", timeout: int = 10) -> Dict[str, Any]:
    """Perform an HTTP smoke test against a running service.

    Sends a GET request and checks that:
    - The response status code is 200.
    - The response body does not contain a known default/placeholder page.

    Args:
        url: URL to test (default: http://localhost:3000/).
        timeout: Request timeout in seconds (default: 10).
    """
    default_pages = ["It works!", "Welcome to nginx", "Apache2 Default", "Default Web Page"]
    try:
        resp = requests.get(url, timeout=timeout)
        is_default = any(d in resp.text for d in default_pages)
        passed = resp.status_code == 200 and not is_default
        return {
            "url": url,
            "status_code": resp.status_code,
            "is_default_page": is_default,
            "body_preview": resp.text[:300],
            "PASS": passed,
            "message": "✅ Smoke test passed" if passed else (
                "❌ Default page detected" if is_default else f"❌ Status {resp.status_code}"
            ),
        }
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "url": url,
            "status_code": None,
            "is_default_page": False,
            "body_preview": "",
            "PASS": False,
            "message": f"❌ Connection failed: {exc}",
        }


@tool
def run_test_script(script_path: str, timeout: int = 120) -> Dict[str, Any]:
    """Execute a test runner script and capture its output.

    The script must be executable (chmod +x).  Results include stdout, stderr,
    and exit code so the agent can report on test outcomes.

    Args:
        script_path: Path to the test runner script (e.g. output/test_runner.sh).
        timeout: Maximum seconds to wait for the tests to complete (default: 120).
    """
    p = Path(script_path)
    if not p.exists():
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Script not found: {script_path}",
        }
    if not os.access(p, os.X_OK):
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Script is not executable: {script_path}. Run: chmod +x {script_path}",
        }
    try:
        result = subprocess.run(
            [str(p.resolve())],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Test script timed out after {timeout} seconds",
        }
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
        }
