#!/usr/bin/env bash
# Build and deploy landing page (syncapp.tech)
# Usage: bash deploy/deploy-landing.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SERVER="root@REDACTED_VPS_IP"
REMOTE_DIR="/opt/services/landing"
COMPOSE_SRC="${SCRIPT_DIR}/compose/landing"
FRONTEND_DIR="${REPO_ROOT}/frontend"

echo "=== Deploy Landing Page ==="

# Build frontend
echo "[*] Building Astro site..."
cd "${FRONTEND_DIR}"
pnpm install --frozen-lockfile
pnpm build
cd "${REPO_ROOT}"

if [ ! -d "${FRONTEND_DIR}/dist" ]; then
    echo "[ERROR] Build failed: dist/ not found"
    exit 1
fi

# Upload compose file + nginx config
echo "[*] Uploading compose config..."
rsync -avz \
    "${COMPOSE_SRC}/docker-compose.yml" \
    "${SERVER}:${REMOTE_DIR}/"

rsync -avz \
    "${REPO_ROOT}/docker/nginx.conf" \
    "${SERVER}:${REMOTE_DIR}/nginx.conf"

# Upload built site
echo "[*] Uploading static files..."
rsync -avz --delete \
    "${FRONTEND_DIR}/dist/" \
    "${SERVER}:${REMOTE_DIR}/dist/"

# Restart container
echo "[*] Restarting landing container..."
ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose up -d"

echo ""
echo "[OK] Landing page deployed"
echo "[!] Verify: curl -I https://syncapp.tech"
