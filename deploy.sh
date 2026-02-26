#!/bin/bash
# Automated deployment script for syncapp.tech landing page to Hostinger

set -e  # Exit on any error

# Configuration
SERVER_IP="187.124.9.212"
SERVER_USER="root"
SERVER_PATH="/home/syncapp/public_html"
DOMAIN="syncapp.tech"
LOCAL_DIST="frontend/dist"

echo "🚀 Starting deployment to Hostinger..."
echo ""

# Step 1: Build frontend
echo "📦 Building landing page..."
cd frontend
pnpm install
pnpm build
cd ..

if [ ! -d "$LOCAL_DIST" ]; then
  echo "❌ Error: dist folder not found!"
  exit 1
fi

echo "✅ Build complete"
echo ""

# Step 2: Upload to server
echo "📤 Uploading files to $SERVER_IP..."
echo "   → Destination: $SERVER_PATH"
echo ""

scp -r "$LOCAL_DIST"/* "$SERVER_USER@$SERVER_IP:$SERVER_PATH/" || {
  echo "❌ SCP upload failed. Check SSH access and server IP."
  exit 1
}

echo "✅ Files uploaded successfully"
echo ""

# Step 3: Verify deployment
echo "🔍 Verifying deployment..."
ssh "$SERVER_USER@$SERVER_IP" "ls -la $SERVER_PATH/index.html" || {
  echo "❌ Verification failed"
  exit 1
}

echo "✅ index.html found on server"
echo ""

# Step 4: Summary
echo "================================================"
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "================================================"
echo ""
echo "📍 Your site is now deployed:"
echo "   → SSH: ssh $SERVER_USER@$SERVER_IP"
echo "   → Path: $SERVER_PATH"
echo "   → Domain: https://$DOMAIN"
echo ""
echo "⚠️  NEXT STEPS:"
echo "   1. Point domain to Hostinger nameservers"
echo "   2. Wait 10-30 minutes for DNS propagation"
echo "   3. Visit https://$DOMAIN to verify"
echo ""
echo "💡 To redeploy later, just run: bash deploy.sh"
echo ""
