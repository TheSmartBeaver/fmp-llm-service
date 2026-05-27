#!/bin/bash
set -e

VPS_HOST="root@72.62.26.202"
VPS_DIR="/opt/fmp-llm-service-debug"
CONTAINER_NAME="fmp-llm-service-debug"

echo "==> Syncing source to VPS..."
rsync -az --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='dl_models' \
  ./ "$VPS_HOST:$VPS_DIR/"

echo "==> Copying .env from prod..."
ssh "$VPS_HOST" "cp /opt/fmp-llm-service/.env $VPS_DIR/.env"

echo "==> Removing existing debug containers..."
ssh "$VPS_HOST" "docker rm -f $CONTAINER_NAME fmp-celery-worker fmp-redis 2>/dev/null || true"

echo "==> Building and starting debug stack on VPS..."
ssh "$VPS_HOST" "cd $VPS_DIR && docker compose -f docker-compose.debug.yml up --build -d"

echo "==> Container logs (last 20 lines):"
ssh "$VPS_HOST" "docker logs --tail 20 $CONTAINER_NAME 2>&1"

echo ""
echo "==> Debug ready. Open SSH tunnel in a terminal:"
echo "    ssh -L 5678:localhost:5678 root@72.62.26.202 -N"
echo "Then launch 'Python: Remote Debug (VPS)' in VS Code."
