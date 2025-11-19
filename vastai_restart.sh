#!/bin/bash

# ============================================
# Restart Vast.ai Container
# ============================================

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/vastai_config.json"
INSTANCE_ID="${VAST_INSTANCE_ID:-}"

# Load config
if [ -f "$CONFIG_FILE" ]; then
    INSTANCE_ID=$(jq -r '.instance_id // empty' "$CONFIG_FILE")
fi

# Get instance ID
if [ -z "$INSTANCE_ID" ]; then
    read -p "Enter Vast.ai instance ID: " INSTANCE_ID
fi

echo -e "${BLUE}🔄 Restarting container on instance $INSTANCE_ID...${NC}"

# Get SSH connection details
SSH_URL=$(vastai ssh-url "$INSTANCE_ID" 2>/dev/null | tr -d '\n\r')
SSH_HOST=$(echo "$SSH_URL" | sed -E 's|ssh://root@([^:]+):.*|\1|')
SSH_PORT=$(echo "$SSH_URL" | sed -E 's|ssh://root@[^:]+:([0-9]+)|\1|')

# Restart container
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" bash << 'ENDSSH'
    echo "Stopping container..."
    docker stop logo-generator

    echo "Starting container..."
    docker start logo-generator

    echo "✅ Container restarted"
    echo ""
    echo "Waiting for server to start..."
    sleep 10

    echo "📋 Recent logs:"
    docker logs logo-generator --tail 30
ENDSSH

echo -e "${GREEN}✅ Restart complete!${NC}"

