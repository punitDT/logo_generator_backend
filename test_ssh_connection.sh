#!/bin/bash

# ============================================
# Test SSH Connection to Vast.ai Instance
# ============================================
# Quick test to verify SSH connection works

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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 Testing SSH Connection${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get SSH URL
echo "Getting SSH connection details..."
SSH_URL=$(vastai ssh-url "$INSTANCE_ID" 2>/dev/null | tr -d '\n\r')

if [ -z "$SSH_URL" ]; then
    echo -e "${RED}❌ Failed to get SSH URL${NC}"
    exit 1
fi

echo "SSH URL: $SSH_URL"

# Parse SSH URL
SSH_HOST=$(echo "$SSH_URL" | sed -E 's|ssh://root@([^:]+):.*|\1|')
SSH_PORT=$(echo "$SSH_URL" | sed -E 's|ssh://root@[^:]+:([0-9]+)|\1|')

echo "SSH Host: $SSH_HOST"
echo "SSH Port: $SSH_PORT"
echo ""

# Test connection
echo "Testing SSH connection..."
if ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -p "$SSH_PORT" "root@$SSH_HOST" "echo 'Connection successful!'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection works!${NC}"
    echo ""
    
    # Get some basic info
    echo "Instance information:"
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" bash << 'EOF'
        echo "  Hostname: $(hostname)"
        echo "  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"
        echo "  CUDA: $(nvcc --version 2>/dev/null | grep release | awk '{print $5}' | tr -d ',')"
        echo "  Docker: $(docker --version | awk '{print $3}' | tr -d ',')"
EOF
    
    echo ""
    echo -e "${GREEN}🎉 Ready to deploy!${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check if instance is running: vastai show instances"
    echo "  2. Verify instance ID is correct"
    echo "  3. Check your SSH key is added to Vast.ai"
    exit 1
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo "Next step: Run ./deploy_vastai.sh to deploy"
echo -e "${BLUE}========================================${NC}"

