#!/bin/bash

# ============================================
# Vast.ai Docker Deployment Script
# ============================================
# Installs Docker if needed and deploys the app

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/vastai_config.json"
ENV_FILE="${SCRIPT_DIR}/.env"

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Load instance ID from config
INSTANCE_ID=$(jq -r '.instance_id' "$CONFIG_FILE")

if [ -z "$INSTANCE_ID" ]; then
    print_error "No instance ID found in config"
    exit 1
fi

print_info "Using instance ID: $INSTANCE_ID"

# Get SSH connection details
print_info "Getting SSH connection details..."
INSTANCE_INFO=$(vastai show instances --raw | jq -r ".[] | select(.id == $INSTANCE_ID)")

if [ -z "$INSTANCE_INFO" ]; then
    print_error "Instance $INSTANCE_ID not found"
    exit 1
fi

# Try to get SSH URL first
SSH_URL=$(vastai ssh-url "$INSTANCE_ID" 2>/dev/null | tr -d '\n\r')

if [ -n "$SSH_URL" ] && [[ "$SSH_URL" != *"error"* ]]; then
    # Parse SSH URL (format: ssh://root@host:port)
    SSH_HOST=$(echo "$SSH_URL" | sed -E 's|ssh://root@([^:]+):.*|\1|')
    SSH_PORT=$(echo "$SSH_URL" | sed -E 's|ssh://root@[^:]+:([0-9]+)|\1|')
else
    # Fallback to machine direct SSH port
    print_info "Using machine direct SSH port..."
    SSH_HOST=$(echo "$INSTANCE_INFO" | jq -r '.public_ipaddr')
    SSH_PORT=$(echo "$INSTANCE_INFO" | jq -r '.machine_dir_ssh_port')
fi

if [ -z "$SSH_HOST" ] || [ -z "$SSH_PORT" ] || [ "$SSH_HOST" = "null" ] || [ "$SSH_PORT" = "null" ]; then
    print_error "Failed to get SSH connection details"
    exit 1
fi

print_info "SSH: root@${SSH_HOST}:${SSH_PORT}"

# Copy .env file first
print_info "Copying .env file..."
if [ -f "$ENV_FILE" ]; then
    scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P "$SSH_PORT" "$ENV_FILE" "root@$SSH_HOST:~/.env.tmp"
    print_success ".env file copied"
else
    print_error ".env file not found"
    exit 1
fi

# Run all deployment steps in a single SSH session
print_info "Running deployment on instance..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" bash << 'ENDSSH'
set -e

echo "========================================="
echo "📦 Docker Deployment"
echo "========================================="

# Step 1: Check and install Docker if needed
echo ""
echo "🐳 Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found, installing..."
    
    # Update package list
    apt-get update -qq
    
    # Install prerequisites
    apt-get install -y -qq ca-certificates curl gnupg lsb-release
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

# Start Docker daemon manually (systemd not available in container)
echo "Starting Docker daemon..."
dockerd > /dev/null 2>&1 &
sleep 5

# Wait for Docker to be ready
for i in {1..30}; do
    if docker info > /dev/null 2>&1; then
        echo "✅ Docker daemon is running"
        break
    fi
    echo "Waiting for Docker daemon... ($i/30)"
    sleep 1
done

docker --version

# Step 2: Setup repository
echo ""
echo "📂 Step 2: Setting up repository..."
if [ -d "logo_generator_backend" ]; then
    echo "Repository exists, pulling latest changes..."
    cd logo_generator_backend
    git pull
    cd ..
else
    echo "Cloning repository..."
    git clone https://github.com/punitDT/logo_generator_backend.git
fi

# Move .env file
mv ~/.env.tmp logo_generator_backend/.env
echo "✅ Repository ready"
ENDSSH

print_success "Docker installation and repository setup complete"

# Continue with Docker build and deployment
print_info "Building and deploying Docker container..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p "$SSH_PORT" "root@$SSH_HOST" bash << 'ENDSSH'
set -e

# Step 3: Build Docker image
echo ""
echo "🔨 Step 3: Building Docker image..."
cd logo_generator_backend
docker build -t logo-generator-gpu .
echo "✅ Docker image built"

# Step 4: Stop existing container
echo ""
echo "🛑 Step 4: Stopping existing container..."
if docker ps -a | grep -q logo-generator; then
    docker stop logo-generator 2>/dev/null || true
    docker rm logo-generator 2>/dev/null || true
    echo "✅ Old container removed"
else
    echo "No existing container found"
fi

# Step 5: Start new container
echo ""
echo "🚀 Step 5: Starting new container..."
docker run -d \
    --name logo-generator \
    --gpus all \
    -p 7860:7860 \
    -v $(pwd)/.env:/app/.env \
    -v /root/.cache/huggingface:/root/.cache/huggingface \
    --restart unless-stopped \
    logo-generator-gpu

echo "✅ Container started"

# Wait for server to start
echo ""
echo "⏳ Waiting for server to start..."
sleep 15

# Show logs
echo ""
echo "📋 Container logs:"
docker logs logo-generator --tail 50

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
ENDSSH

# Get public IP for access info
PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.public_ipaddr')

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
echo "📋 View logs:"
echo "   ssh -p ${SSH_PORT} root@${PUBLIC_IP} 'docker logs -f logo-generator'"
echo ""

