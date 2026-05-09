---
name: code-interpreter
description: Safe Python code execution in an isolated subprocess. Use when the agent needs to run calculations, transform data programmatically, or test logic.
metadata:
  author: agent-builder
  version: "1.0.0"
---

# Code Interpreter Skill

Gives agents the ability to execute Python code in an isolated subprocess with a timeout. Useful for calculations, data transformations, and algorithmic tasks.

## Tools

- **run_python(code)** — Execute Python code and return stdout/stderr (10s timeout)
- **install_package(name)** — pip install a package into the agent's environment

## Security

Code runs in a subprocess with:
- 10-second timeout (configurable)
- No network access by default
- Sandboxed to workspace directory

## Configuration

```toml
[skills.code-interpreter]
timeout_seconds = 10
allowed_imports = ["math", "statistics", "datetime", "json", "re", "collections", "itertools", "functools", "decimal", "fractions", "random"]
```
