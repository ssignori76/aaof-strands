"""File tools — @tool functions for reading, writing, and inspecting files."""
import os
from pathlib import Path
from typing import Any, Dict, List

from strands import tool


@tool
def read_file(path: str) -> Dict[str, Any]:
    """Read the contents of a file.

    Args:
        path: Absolute or relative path to the file to read.
    """
    p = Path(path)
    if not p.exists():
        return {"success": False, "error": f"File not found: {path}"}
    try:
        content = p.read_text(encoding="utf-8")
        return {"success": True, "content": content, "size": p.stat().st_size}
    except Exception as exc:  # pylint: disable=broad-except
        return {"success": False, "error": str(exc)}


@tool
def write_file(path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
    """Write content to a file, creating parent directories as needed.

    Args:
        path: Absolute or relative path to the file to write.
        content: Text content to write.
        overwrite: If False and file exists, return an error (default: True).
    """
    p = Path(path)
    if not overwrite and p.exists():
        return {"success": False, "error": f"File already exists and overwrite=False: {path}"}
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(p), "size": p.stat().st_size}
    except Exception as exc:  # pylint: disable=broad-except
        return {"success": False, "error": str(exc)}


@tool
def list_directory(path: str = ".", recursive: bool = False) -> Dict[str, Any]:
    """List files and directories inside a given path.

    Args:
        path: Directory path to list (default: current directory).
        recursive: If True, list recursively (default: False).
    """
    p = Path(path)
    if not p.is_dir():
        return {"success": False, "error": f"Not a directory: {path}"}
    try:
        if recursive:
            entries: List[str] = [str(f) for f in p.rglob("*")]
        else:
            entries = [str(f) for f in p.iterdir()]
        return {"success": True, "entries": sorted(entries), "count": len(entries)}
    except Exception as exc:  # pylint: disable=broad-except
        return {"success": False, "error": str(exc)}


@tool
def check_file_exists(path: str) -> Dict[str, Any]:
    """Check whether a file exists and return its metadata.

    Args:
        path: Path to the file to check.
    """
    p = Path(path)
    exists = p.exists()
    result: Dict[str, Any] = {"exists": exists, "path": str(p)}
    if exists:
        stat = p.stat()
        result["size"] = stat.st_size
        result["is_file"] = p.is_file()
        result["is_dir"] = p.is_dir()
        result["executable"] = os.access(p, os.X_OK)
    return result


@tool
def append_to_file(path: str, content: str) -> Dict[str, Any]:
    """Append content to an existing file (or create it if it doesn't exist).

    Args:
        path: Path to the file.
        content: Text to append.
    """
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(content)
        return {"success": True, "path": str(p), "size": p.stat().st_size}
    except Exception as exc:  # pylint: disable=broad-except
        return {"success": False, "error": str(exc)}
