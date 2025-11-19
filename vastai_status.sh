#!/bin/bash

# ============================================
# Check Vast.ai Deployment Status
# ============================================

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📊 Deployment Status${NC}"
echo -e "${BLUE}========================================${NC}"

# Get instance info
echo -e "${BLUE}🖥️  Instance Information:${NC}"
INSTANCE_INFO=$(vastai show instance "$INSTANCE_ID" --raw)
PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.public_ipaddr')
SSH_PORT=$(echo "$INSTANCE_INFO" | jq -r '.ssh_port')
GPU_NAME=$(echo "$INSTANCE_INFO" | jq -r '.gpu_name')
CUDA_VERSION=$(echo "$INSTANCE_INFO" | jq -r '.cuda_max_good')

echo "   Instance ID: $INSTANCE_ID"
echo "   Public IP: $PUBLIC_IP"
echo "   SSH Port: $SSH_PORT"
echo "   GPU: $GPU_NAME"
echo "   CUDA: $CUDA_VERSION"
echo ""

# Get SSH connection details
SSH_URL=$(vastai ssh-url "$INSTANCE_ID" 2>/dev/null | tr -d '\n\r')
SSH_HOST=$(echo "$SSH_URL" | sed -E 's|ssh://root@([^:]+):.*|\1|')
SSH_PORT=$(echo "$SSH_URL" | sed -E 's|ssh://root@[^:]+:([0-9]+)|\1|')

# Check container status
echo -e "${BLUE}🐳 Container Status:${NC}"
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" bash << 'ENDSSH'
    if docker ps | grep -q logo-generator; then
        echo "   Status: ✅ Running"
        echo ""
        echo "   Container Details:"
        docker ps --filter name=logo-generator --format "   ID: {{.ID}}\n   Image: {{.Image}}\n   Status: {{.Status}}\n   Ports: {{.Ports}}"
    else
        echo "   Status: ❌ Not Running"
        if docker ps -a | grep -q logo-generator; then
            echo "   (Container exists but is stopped)"
        fi
    fi
ENDSSH

echo ""

# Check API health
echo -e "${BLUE}🏥 API Health Check:${NC}"
HEALTH_URL="http://${PUBLIC_IP}:7860/health"
echo "   Checking: $HEALTH_URL"

if curl -s -f "$HEALTH_URL" > /tmp/health_response.json 2>/dev/null; then
    echo -e "   ${GREEN}✅ API is healthy${NC}"
    echo ""
    echo "   Response:"
    cat /tmp/health_response.json | jq '.' 2>/dev/null || cat /tmp/health_response.json
else
    echo -e "   ${RED}❌ API is not responding${NC}"
fi

echo ""

# GPU stats
echo -e "${BLUE}🎮 GPU Status:${NC}"
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" bash << 'ENDSSH'
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | \
    awk -F', ' '{printf "   GPU: %s\n   Memory: %s MB / %s MB (%.1f%%)\n   Utilization: %s%%\n", $1, $2, $3, ($2/$3)*100, $4}'
ENDSSH

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}📍 Access URLs:${NC}"
echo "   API: http://${PUBLIC_IP}:7860"
echo "   Docs: http://${PUBLIC_IP}:7860/docs"
echo "   Health: http://${PUBLIC_IP}:7860/health"
echo -e "${BLUE}========================================${NC}"

