# Infrastructure Setup (systemd + Docker Compose)

Pattern for running agent infrastructure as systemd-managed services that auto-start on boot.

## Service Architecture

```
┌─────────────────────────────────────────────┐
│ systemd --user                               │
│                                              │
│  ┌─ langfuse.service ─────────────────────┐  │
│  │  Type=oneshot                           │  │
│  │  docker compose up -d (6 containers)    │  │
│  │  ├─ postgres (127.0.0.1:5432)           │  │
│  │  ├─ clickhouse (127.0.0.1:8123/9000)    │  │
│  │  ├─ redis (127.0.0.1:6379)              │  │
│  │  ├─ minio (9090/9091)                   │  │
│  │  ├─ langfuse-web (:3000)                │  │
│  │  └─ langfuse-worker (:3030)             │  │
│  └─────────────────────────────────────────┘  │
│           │ depends on                         │
│           ▼                                    │
│  ┌─ a-share-options-agent.service ──────────┐  │
│  │  Type=simple                              │  │
│  │  python -m src.main                       │  │
│  │  ├─ FastAPI (:8080)                       │  │
│  │  └─ Telegram Bot (polling)                │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Service Files

### Docker Compose Service (langfuse.service)

```ini
# ~/.config/systemd/user/langfuse.service
[Unit]
Description=Langfuse observability stack (Docker Compose)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/project
ExecStartPre=-docker compose -f infra/docker-compose.langfuse.yml down --remove-orphans
ExecStart=docker compose -f infra/docker-compose.langfuse.yml up -d --wait --wait-timeout 120
ExecStop=docker compose -f infra/docker-compose.langfuse.yml down
ExecStartPost=/bin/bash -c 'for i in {1..30}; do curl -s -o /dev/null http://localhost:3000 && exit 0; sleep 2; done; exit 1'

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

Key decisions:
- **`Type=oneshot` + `RemainAfterExit=yes`**: `docker compose up -d` exits immediately after starting containers. `RemainAfterExit` tells systemd the service is still "active" even though the main process exited.
- **`ExecStartPre=-`**: The `-` prefix means "ignore failure" — if there are no orphan containers from a previous run, that's fine.
- **`ExecStartPost`**: Health check that waits for the web UI to be reachable. Fails the service start if Langfuse doesn't come up within 60s.
- **`Requires=docker.service`**: Ensures Docker daemon is running before attempting to start containers.

### Agent Service (a-share-options-agent.service)

```ini
# ~/.config/systemd/user/<agent-name>.service
[Unit]
Description=Agent Name (FastAPI + Telegram Bot)
After=network-online.target langfuse.service
Wants=network-online.target langfuse.service

[Service]
Type=simple
WorkingDirectory=/path/to/project
EnvironmentFile=/path/to/project/.env
ExecStart=/path/to/project/.venv/bin/python -m src.main
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=<agent-name>

[Install]
WantedBy=default.target
```

Key decisions:
- **`After=langfuse.service`**: Agent waits for Langfuse to be healthy before starting (prevents startup race conditions).
- **`EnvironmentFile=.env`**: Secrets loaded from a separate file, never committed to git.
- **`Restart=on-failure`**: Auto-restart if the Python process crashes. 5s backoff to avoid tight crash loops.
- **`SyslogIdentifier`**: Makes `journalctl --user -u <name>` output easier to filter.

## Setup Script Pattern

The `infra/setup.sh` script handles first-time provisioning:

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. Install Docker Compose plugin if missing
if ! docker compose version &>/dev/null; then
    sudo apt-get install -y docker-compose-plugin
fi

# 2. Add user to docker group
sudo usermod -aG docker "$USER"

# 3. Create .env from .env.example
cp -n .env.example .env

# 4. Install systemd units to ~/.config/systemd/user/
cp infra/langfuse.service ~/.config/systemd/user/
cp infra/agent.service ~/.config/systemd/user/

# 5. Enable and start
systemctl --user daemon-reload
systemctl --user enable --now langfuse.service
systemctl --user enable --now agent.service
```

## Commands Cheat Sheet

```bash
# Status
systemctl --user status langfuse
systemctl --user status a-share-options-agent

# Logs (follow tail)
journalctl --user -u langfuse -f
journalctl --user -u a-share-options-agent -f

# Restart after code change
systemctl --user restart a-share-options-agent

# Stop everything
systemctl --user stop a-share-options-agent langfuse

# Disable auto-start
systemctl --user disable langfuse a-share-options-agent
```

## When to Use Self-Hosted vs Cloud

### Use Langfuse Cloud (free tier) when:
- Single developer, low event volume
- Don't want to manage 6 Docker containers
- OK with data leaving your server

Config:
```toml
[langfuse]
host = "https://cloud.langfuse.com"
```

### Use Self-Hosted when:
- Need unlimited events/users
- Data residency requirements
- Already running Docker for other services
- Custom retention policies needed

Config:
```toml
[langfuse]
host = "http://localhost:3000"
```

## Lingering User Sessions

By default, `systemd --user` services die when the user's last session exits. To keep services running after logout:

```bash
sudo loginctl enable-linger $USER
```

This is critical for servers — without linger, all user services stop when you disconnect SSH.

## Docker Compose v2 Note

Always use `docker compose` (v2 plugin), not `docker-compose` (v1 Python). The v2 plugin is maintained, faster, and uses the same Compose Spec. Install via:

```bash
sudo apt-get install docker-compose-plugin
```
