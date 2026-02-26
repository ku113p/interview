#!/usr/bin/env bash
# Deploy interview product to VPS (manual fallback / first-time setup)
# After initial setup, git push to main triggers auto-deploy via CI + Watchtower.
#
# Usage: bash deploy/deploy-interview.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER="root@187.124.9.212"
REMOTE_DIR="/opt/services/interview"
COMPOSE_SRC="${SCRIPT_DIR}/compose/interview"

echo "=== Deploy Interview Product ==="

# Upload compose file
echo "[*] Uploading compose config..."
rsync -avz \
    "${COMPOSE_SRC}/docker-compose.yml" \
    "${SERVER}:${REMOTE_DIR}/"

# Pull latest images from GHCR and restart
echo "[*] Pulling images and starting services..."
ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose pull && docker compose up -d"

echo ""
echo "[*] Container status:"
ssh "$SERVER" "docker ps --filter 'name=interview-' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo ""
echo "[OK] Interview product deployed"
echo "[!] Verify promo:   curl -I https://promo.interview.syncapp.tech"
echo "[!] Verify backend: curl -I https://api.interview.syncapp.tech"
echo "[!] Verify MCP:     curl -I https://mcp.interview.syncapp.tech"
