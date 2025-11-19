#!/bin/bash

# ============================================
# Vast.ai Instance Setup Helper
# ============================================
# This script helps you configure your Vast.ai instance ID

set -e

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CONFIG_FILE="vastai_config.json"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔧 Vast.ai Instance Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if vastai CLI is installed
if ! command -v vastai &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vast.ai CLI not found!${NC}"
    echo "Install it with: pip install vastai"
    echo ""
    read -p "Install now? (y/n): " install_choice
    if [ "$install_choice" = "y" ]; then
        pip install vastai
        echo -e "${GREEN}✅ Vast.ai CLI installed${NC}"
    else
        echo "Please install vastai CLI and run this script again"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Vast.ai CLI found${NC}"
echo ""

# Check if API key is configured
echo "Checking Vast.ai API key..."
if vastai show instances &> /dev/null; then
    echo -e "${GREEN}✅ API key is configured${NC}"
else
    echo -e "${YELLOW}⚠️  API key not configured${NC}"
    echo ""
    echo "Get your API key from: https://cloud.vast.ai/account/"
    echo ""
    read -p "Enter your Vast.ai API key: " api_key
    vastai set api-key "$api_key"
    echo -e "${GREEN}✅ API key configured${NC}"
fi

echo ""
echo -e "${BLUE}📋 Your Vast.ai Instances:${NC}"
echo ""

# List instances
vastai show instances

echo ""
echo -e "${BLUE}========================================${NC}"
read -p "Enter the instance ID you want to use: " instance_id

if [ -z "$instance_id" ]; then
    echo -e "${YELLOW}No instance ID provided${NC}"
    exit 1
fi

# Verify instance exists
echo ""
echo "Verifying instance $instance_id..."
if vastai show instance "$instance_id" &> /dev/null; then
    echo -e "${GREEN}✅ Instance $instance_id is accessible${NC}"
    
    # Get instance details
    INSTANCE_INFO=$(vastai show instance "$instance_id" --raw)
    GPU_NAME=$(echo "$INSTANCE_INFO" | jq -r '.gpu_name')
    PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.public_ipaddr')
    
    echo ""
    echo "Instance Details:"
    echo "  GPU: $GPU_NAME"
    echo "  IP: $PUBLIC_IP"
else
    echo -e "${YELLOW}⚠️  Cannot access instance $instance_id${NC}"
    echo "Please check the instance ID and try again"
    exit 1
fi

# Update config file
echo ""
echo "Updating $CONFIG_FILE..."

# Read existing config or create new one
if [ -f "$CONFIG_FILE" ]; then
    jq --arg id "$instance_id" '.instance_id = $id' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp"
    mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
else
    cat > "$CONFIG_FILE" << EOF
{
  "instance_id": "$instance_id",
  "image_name": "logo-generator-gpu",
  "container_name": "logo-generator",
  "app_port": 7860
}
EOF
fi

echo -e "${GREEN}✅ Configuration saved to $CONFIG_FILE${NC}"

# Ask about environment file
echo ""
echo -e "${BLUE}========================================${NC}"
echo "Environment Configuration"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ ! -f ".env" ]; then
    echo "No .env file found."
    read -p "Copy production template (.env.vastai) to .env? (y/n): " copy_env
    if [ "$copy_env" = "y" ]; then
        cp .env.vastai .env
        echo -e "${GREEN}✅ Created .env from template${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  Please edit .env and add your HuggingFace token if needed${NC}"
        echo "   HF_TOKEN=your_token_here"
    fi
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Review/edit .env file (optional)"
echo "  2. Run deployment: ./deploy_vastai.sh"
echo "  3. Check status: ./vastai_status.sh"
echo ""
echo "Instance ID: $instance_id"
echo "Config file: $CONFIG_FILE"
echo ""

