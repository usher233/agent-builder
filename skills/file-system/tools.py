import os
from pathlib import Path
from langchain_core.tools import tool

WORKSPACE = Path(os.getenv("SKILLS_WORKSPACE", "./workspace")).resolve()
MAX_FILE_SIZE = int(os.getenv("SKILLS_MAX_FILE_MB", "10")) * 1024 * 1024


def _safe_path(user_path: str) -> Path:
    """Resolve a user-provided path within the workspace. Raises on escape attempts."""
    resolved = (WORKSPACE / user_path).resolve()
    if not str(resolved).startswith(str(WORKSPACE)):
        raise ValueError(f"Path traversal blocked: {user_path}")
    return resolved


@tool
def read_file(path: str, max_lines: int = 500) -> str:
    """Read a text file from the workspace. Returns content with line numbers."""
    try:
        full_path = _safe_path(path)
        if not full_path.exists():
            return f"File not found: {path}"
        if full_path.stat().st_size > MAX_FILE_SIZE:
            return f"File too large (> {MAX_FILE_SIZE // 1024 // 1024} MB): {path}"

        content = full_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append(f"\n... (truncated {len(content.split(chr(10))) - max_lines} more lines)")

        numbered = [f"{i + 1:4d} | {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered)
    except ValueError as e:
        return str(e)
    except UnicodeDecodeError:
        return f"Binary file cannot be read as text: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file in the workspace. Creates parent directories as needed."""
    try:
        full_path = _safe_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        return f"Written {len(content)} chars to {path}"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def list_dir(path: str = ".") -> str:
    """List files and directories in a workspace directory."""
    try:
        full_path = _safe_path(path)
        if not full_path.exists():
            return f"Directory not found: {path}"
        if not full_path.is_dir():
            return f"Not a directory: {path}"

        entries = []
        for entry in sorted(full_path.iterdir()):
            suffix = "/" if entry.is_dir() else ""
            size = entry.stat().st_size if entry.is_file() else 0
            size_str = f"{size:>8d}" if size < 1024 else f"{size / 1024:>7.1f}K"
            entries.append(f"  {size_str}  {entry.name}{suffix}")

        return f"Contents of {path}:\n" + "\n".join(entries) if entries else f"Empty directory: {path}"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error listing directory: {e}"


def get_tools():
    return [read_file, write_file, list_dir]
