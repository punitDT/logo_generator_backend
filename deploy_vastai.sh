#!/bin/bash

# ============================================
# Vast.ai Deployment Script for Logo Generator
# ============================================
# This script automates deployment to Vast.ai GPU instances
# Prerequisites: vastai CLI installed and configured

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/vastai_config.json"
ENV_FILE="${SCRIPT_DIR}/.env"

# Default values (can be overridden by config file)
INSTANCE_ID="${VAST_INSTANCE_ID:-}"
IMAGE_NAME="logo-generator-gpu"
CONTAINER_NAME="logo-generator"
APP_PORT=7860
GITHUB_REPO="https://github.com/punitDT/logo_generator_backend.git"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if vastai CLI is installed
check_vastai_cli() {
    if ! command -v vastai &> /dev/null; then
        print_error "Vast.ai CLI not found!"
        echo "Install it with: pip install vastai"
        exit 1
    fi
    print_success "Vast.ai CLI found"
}

# Load configuration
load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        print_info "Loading configuration from $CONFIG_FILE"
        INSTANCE_ID=$(jq -r '.instance_id // empty' "$CONFIG_FILE")
        IMAGE_NAME=$(jq -r '.image_name // "logo-generator-gpu"' "$CONFIG_FILE")
        CONTAINER_NAME=$(jq -r '.container_name // "logo-generator"' "$CONFIG_FILE")
    fi
}

# Get instance ID from user or config
get_instance_id() {
    if [ -z "$INSTANCE_ID" ]; then
        echo ""
        print_warning "No instance ID configured"
        echo "You can:"
        echo "  1. Set VAST_INSTANCE_ID environment variable"
        echo "  2. Create vastai_config.json with instance_id"
        echo "  3. Enter it now"
        echo ""
        read -p "Enter Vast.ai instance ID: " INSTANCE_ID
        
        if [ -z "$INSTANCE_ID" ]; then
            print_error "Instance ID is required"
            exit 1
        fi
    fi
    print_success "Using instance ID: $INSTANCE_ID"
}

# Check instance status
check_instance() {
    print_info "Checking instance status..."
    if vastai show instance "$INSTANCE_ID" &> /dev/null; then
        print_success "Instance $INSTANCE_ID is accessible"
        return 0
    else
        print_error "Cannot access instance $INSTANCE_ID"
        return 1
    fi
}

# Get SSH connection details
get_ssh_command() {
    # Get SSH URL from vastai (format: ssh://root@host:port)
    SSH_URL=$(vastai ssh-url "$INSTANCE_ID" 2>/dev/null | tr -d '\n\r')

    if [ -z "$SSH_URL" ]; then
        print_error "Failed to get SSH URL for instance $INSTANCE_ID"
        exit 1
    fi

    # Parse SSH URL to extract host and port
    # Format: ssh://root@ssh9.vast.ai:21877
    SSH_HOST=$(echo "$SSH_URL" | sed -E 's|ssh://root@([^:]+):.*|\1|')
    SSH_PORT=$(echo "$SSH_URL" | sed -E 's|ssh://root@[^:]+:([0-9]+)|\1|')

    if [ -z "$SSH_HOST" ] || [ -z "$SSH_PORT" ]; then
        print_error "Failed to parse SSH connection details"
        print_error "SSH URL: $SSH_URL"
        exit 1
    fi

    print_info "SSH Host: $SSH_HOST"
    print_info "SSH Port: $SSH_PORT"
}

# Execute command on remote instance
remote_exec() {
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" "$@"
}

# Deploy application
deploy() {
    print_header "🚀 Deploying Logo Generator to Vast.ai"

    # Check prerequisites
    check_vastai_cli
    load_config
    get_instance_id
    check_instance
    get_ssh_command

    print_header "📦 Deployment Steps"

    # Step 1: Clone/Update repository
    print_info "Step 1: Setting up repository on instance..."
    print_info "Connecting to instance..."

    remote_exec bash << 'ENDSSH'
        set -e
        echo "📂 Setting up repository..."
        
        # Clone or update repository
        if [ -d "logo_generator_backend" ]; then
            echo "Repository exists, pulling latest changes..."
            cd logo_generator_backend
            git pull
        else
            echo "Cloning repository..."
            git clone https://github.com/punitDT/logo_generator_backend.git
            cd logo_generator_backend
        fi
        
        echo "✅ Repository ready"
ENDSSH
    
    print_success "Repository setup complete"
    
    # Step 2: Copy .env file
    print_info "Step 2: Copying environment configuration..."
    if [ -f "$ENV_FILE" ]; then
        scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P "$SSH_PORT" "$ENV_FILE" "root@$SSH_HOST:~/logo_generator_backend/.env"
        print_success "Environment file copied"
    else
        print_warning ".env file not found locally, using default configuration"
    fi

    # Step 3: Build Docker image
    print_info "Step 3: Building Docker image..."
    remote_exec bash << 'ENDSSH'
        set -e
        cd logo_generator_backend
        echo "🔨 Building Docker image..."
        docker build -t logo-generator-gpu .
        echo "✅ Docker image built"
ENDSSH

    print_success "Docker image built successfully"

    # Step 4: Stop existing container (if any)
    print_info "Step 4: Stopping existing container..."
    remote_exec bash << 'ENDSSH'
        if docker ps -a | grep -q logo-generator; then
            echo "Stopping existing container..."
            docker stop logo-generator 2>/dev/null || true
            docker rm logo-generator 2>/dev/null || true
            echo "✅ Old container removed"
        else
            echo "No existing container found"
        fi
ENDSSH

    # Step 5: Run new container
    print_info "Step 5: Starting new container..."
    remote_exec bash << 'ENDSSH'
        set -e
        cd logo_generator_backend
        echo "🚀 Starting container..."
        docker run -d \
            --name logo-generator \
            --gpus all \
            -p 7860:7860 \
            -v $(pwd)/.env:/app/.env \
            -v /root/.cache/huggingface:/root/.cache/huggingface \
            --restart unless-stopped \
            logo-generator-gpu

        echo "✅ Container started"
        echo ""
        echo "Waiting for server to start..."
        sleep 10

        echo "📋 Container logs:"
        docker logs logo-generator --tail 50
ENDSSH
    
    print_success "Container started successfully"
    
    # Get instance details
    print_header "📊 Deployment Complete!"
    print_info "Getting instance details..."
    
    INSTANCE_INFO=$(vastai show instance "$INSTANCE_ID" --raw)
    PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.public_ipaddr')
    SSH_PORT=$(echo "$INSTANCE_INFO" | jq -r '.ssh_port')
    
    echo ""
    print_success "Deployment successful!"
    echo ""
    echo "🌐 Access your API:"
    echo "   API URL: http://${PUBLIC_IP}:7860"
    echo "   API Docs: http://${PUBLIC_IP}:7860/docs"
    echo "   Health Check: http://${PUBLIC_IP}:7860/health"
    echo ""
    echo "🔧 SSH Access:"
    echo "   ssh -p ${SSH_PORT} root@${PUBLIC_IP}"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: ./vastai_logs.sh"
    echo "   Check status: ./vastai_status.sh"
    echo "   Restart: ./vastai_restart.sh"
    echo ""
}

# Main execution
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    *)
        echo "Usage: $0 [deploy]"
        exit 1
        ;;
esac

