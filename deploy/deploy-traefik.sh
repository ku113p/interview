#!/usr/bin/env bash
# Deploy/update Traefik reverse proxy to VPS
# Usage: bash deploy/deploy-traefik.sh [--swap]
#   --swap: Switch from temp ports (8080/8443) to production (80/443)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVER="root@REDACTED_VPS_IP"
REMOTE_DIR="/opt/services/traefik"
COMPOSE_SRC="${SCRIPT_DIR}/compose/traefik"

SWAP_MODE=false
if [[ "${1:-}" == "--swap" ]]; then
    SWAP_MODE=true
fi

echo "=== Deploy Traefik ==="

# Upload config files
echo "[*] Uploading Traefik config..."
rsync -avz --delete \
    "${COMPOSE_SRC}/traefik.yml" \
    "${COMPOSE_SRC}/docker-compose.yml" \
    "${SERVER}:${REMOTE_DIR}/"

rsync -avz --delete \
    "${COMPOSE_SRC}/dynamic/" \
    "${SERVER}:${REMOTE_DIR}/dynamic/"

if $SWAP_MODE; then
    echo "[*] Switching to production ports (80/443)..."
    echo "[*] Stopping nginx..."
    ssh "$SERVER" "systemctl stop nginx && systemctl disable nginx || true"

    echo "[*] Updating Traefik ports..."
    ssh "$SERVER" "cd ${REMOTE_DIR} && \
        sed -i 's/8080:80/80:80/' docker-compose.yml && \
        sed -i 's/8443:443/443:443/' docker-compose.yml"

    echo "[*] Removing temp firewall rules..."
    ssh "$SERVER" "ufw delete allow 8080/tcp || true; ufw delete allow 8443/tcp || true"
fi

echo "[*] Starting Traefik..."
ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose pull && docker compose up -d"

echo "[*] Checking health..."
sleep 3
ssh "$SERVER" "docker ps --filter name=traefik --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

if $SWAP_MODE; then
    echo ""
    echo "[OK] Traefik is now on production ports 80/443"
    echo "[!] Verify: curl -I https://syncapp.tech"
    echo "[!] Rollback: docker compose down && systemctl start nginx"
else
    echo ""
    echo "[OK] Traefik deployed on temp ports 8080/8443"
    echo "[!] Test: curl -k https://localhost:8443 --resolve syncapp.tech:8443:127.0.0.1"
    echo "[!] When ready: bash deploy/deploy-traefik.sh --swap"
fi
