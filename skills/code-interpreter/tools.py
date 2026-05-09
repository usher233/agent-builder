import os
import sys
import subprocess
import tempfile
from pathlib import Path
from langchain_core.tools import tool

TIMEOUT = int(os.getenv("CODE_TIMEOUT", "10"))


@tool
def run_python(code: str) -> str:
    """Execute Python code in an isolated subprocess. Returns stdout and stderr.

    The code has access to the Python standard library. Use for calculations,
    data transformations, and algorithmic tasks. Max 10 seconds execution time.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=str(Path.cwd()),
        )

        output = []
        if result.stdout:
            output.append(result.stdout.strip())
        if result.stderr:
            output.append(f"[stderr]\n{result.stderr.strip()}")
        if result.returncode != 0:
            output.append(f"[exit code: {result.returncode}]")

        return "\n".join(output) if output else "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: code execution timed out after {TIMEOUT}s"
    except Exception as e:
        return f"Error: {e}"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@tool
def install_package(name: str) -> str:
    """Install a Python package using pip. Use this to add dependencies the agent needs."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", name],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return f"Package installed: {name}"
        return f"Installation failed for {name}:\n{result.stderr.strip()}"
    except Exception as e:
        return f"Error installing {name}: {e}"


def get_tools():
    return [run_python, install_package]
