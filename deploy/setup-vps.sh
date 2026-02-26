#!/usr/bin/env bash
# One-time VPS setup: Docker, firewall, directory structure
# Usage: ssh root@REDACTED_VPS_IP 'bash -s' < deploy/setup-vps.sh

set -euo pipefail

SERVER_IP="REDACTED_VPS_IP"
SERVICES_DIR="/opt/services"

echo "=== VPS Setup: Docker + Firewall + Directory Structure ==="
echo ""

# --- Docker ---
if command -v docker &>/dev/null; then
    echo "[OK] Docker already installed: $(docker --version)"
else
    echo "[*] Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
    echo "[OK] Docker installed: $(docker --version)"
fi

# Docker log rotation
echo "[*] Configuring Docker log rotation..."
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "5" }
}
EOF
systemctl restart docker

# --- Directory structure ---
echo "[*] Creating directory structure..."
mkdir -p "${SERVICES_DIR}"/{traefik/{dynamic,acme,logs},landing/dist,interview/{backend,promo-dist,data},monitoring,backup}

# Traefik cert file (must exist with strict permissions)
touch "${SERVICES_DIR}/traefik/acme/acme.json"
chmod 600 "${SERVICES_DIR}/traefik/acme/acme.json"

echo "[OK] Directory structure created at ${SERVICES_DIR}/"

# --- Firewall ---
echo "[*] Configuring firewall..."
if command -v ufw &>/dev/null; then
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp comment 'SSH'
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    # Temp ports for parallel Traefik testing (remove after swap)
    ufw allow 8080/tcp comment 'Traefik temp HTTP'
    ufw allow 8443/tcp comment 'Traefik temp HTTPS'
    echo "y" | ufw enable
    echo "[OK] Firewall configured"
    ufw status numbered
else
    echo "[SKIP] ufw not found, install manually: apt install ufw"
fi

# --- SSH hardening reminder ---
echo ""
echo "=== Manual Steps ==="
echo ""
echo "1. SSH hardening (edit /etc/ssh/sshd_config):"
echo "   PasswordAuthentication no"
echo "   MaxAuthTries 3"
echo "   Then: systemctl restart sshd"
echo ""
echo "2. Set admin password for Dozzle (logs dashboard):"
echo "   apt-get install -y apache2-utils"
echo "   htpasswd -nb admin YOUR_PASSWORD"
echo "   Paste the output into:"
echo "   ${SERVICES_DIR}/traefik/dynamic/middlewares.yml"
echo "   (replace REPLACE_WITH_HTPASSWD_HASH)"
echo ""
echo "3. After the nginx->traefik swap, remove temp firewall rules:"
echo "   ufw delete allow 8080/tcp"
echo "   ufw delete allow 8443/tcp"
echo ""
echo "=== Setup Complete ==="
