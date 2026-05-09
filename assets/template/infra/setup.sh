#!/usr/bin/env bash
set -euo pipefail

echo "=== {{AGENT_NAME}} — Infrastructure Setup ==="

# 1. Install Docker Compose plugin if missing
if ! docker compose version &>/dev/null; then
    echo "Installing docker-compose-plugin..."
    sudo apt-get update -qq
    sudo apt-get install -y docker-compose-plugin
fi

# 2. Add user to docker group if not already
if ! groups "$USER" | grep -q docker; then
    echo "Adding $USER to docker group..."
    sudo usermod -aG docker "$USER"
    echo "⚠️  You may need to log out and back in for docker group to take effect."
fi

# 3. Create .env from .env.example if not present
if [ ! -f .env ]; then
    cp -n .env.example .env
    echo "Created .env from .env.example — fill in your API keys!"
fi

# 4. Create data directory
mkdir -p data workspace

# 5. Install systemd user units
mkdir -p ~/.config/systemd/user/
cp infra/langfuse.service ~/.config/systemd/user/
cp infra/{{AGENT_NAME}}.service ~/.config/systemd/user/

# Replace placeholder with actual project directory
PROJECT_DIR="$(pwd)"
sed -i "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" ~/.config/systemd/user/langfuse.service
sed -i "s|{{PROJECT_DIR}}|$PROJECT_DIR|g" ~/.config/systemd/user/{{AGENT_NAME}}.service

# 6. Reload and enable
systemctl --user daemon-reload
systemctl --user enable --now langfuse.service
systemctl --user enable --now {{AGENT_NAME}}.service

echo ""
echo "=== Setup Complete ==="
echo "Langfuse UI:  http://localhost:3000 (admin@local.dev / admin123)"
echo "Agent Web UI: http://localhost:8080"
echo ""
echo "Useful commands:"
echo "  systemctl --user status {{AGENT_NAME}}"
echo "  journalctl --user -u {{AGENT_NAME}} -f"
echo "  systemctl --user restart {{AGENT_NAME}}"
