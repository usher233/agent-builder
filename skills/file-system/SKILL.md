---
name: file-system
description: Safe file system operations for agents. Use when the agent needs to read, write, or list local files within a sandboxed directory.
metadata:
  author: agent-builder
  version: "1.0.0"
---

# File System Skill

Gives agents safe access to the local file system within a configured workspace directory.

## Tools

- **read_file(path)** — Read a text file, returns content with line numbers
- **write_file(path, content)** — Write content to a file (creates parent dirs)
- **list_dir(path)** — List directory contents with sizes and types

## Security

All paths are resolved relative to the configured workspace root. Path traversal (`../`) outside the workspace is blocked.

## Configuration

```toml
[skills.file-system]
workspace = "./workspace"
max_file_size_mb = 10
```
