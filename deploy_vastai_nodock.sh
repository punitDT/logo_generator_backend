#!/bin/bash

# ============================================
# Vast.ai Deployment Script (No Docker)
# ============================================
# Runs the application directly on the instance

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

SSH_HOST=$(echo "$INSTANCE_INFO" | jq -r '.ssh_host')
SSH_PORT=$(echo "$INSTANCE_INFO" | jq -r '.ssh_port')

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
echo "📦 Starting Deployment (No Docker)"
echo "========================================="

# Step 1: Setup repository
echo ""
echo "📂 Step 1: Setting up repository..."
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

# Step 2: Install dependencies
echo ""
echo "📦 Step 2: Installing Python dependencies..."
cd logo_generator_backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Step 3: Stop existing process
echo ""
echo "🛑 Step 3: Stopping existing process..."
if [ -f "app.pid" ]; then
    OLD_PID=$(cat app.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping process $OLD_PID..."
        kill $OLD_PID || true
        sleep 2
    fi
    rm -f app.pid
    echo "✅ Old process stopped"
else
    echo "No existing process found"
fi

# Step 4: Start new process
echo ""
echo "🚀 Step 4: Starting application..."

# Start the application in the background
nohup venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > app.log 2>&1 &
APP_PID=$!
echo $APP_PID > app.pid

echo "✅ Application started with PID: $APP_PID"

# Wait for server to start
echo ""
echo "⏳ Waiting for server to start..."
sleep 10

# Check if process is still running
if ps -p $APP_PID > /dev/null 2>&1; then
    echo "✅ Process is running"
else
    echo "❌ Process died, check logs:"
    tail -50 app.log
    exit 1
fi

# Show recent logs
echo ""
echo "📋 Application logs:"
tail -30 app.log

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
ENDSSH

# Get public IP and port mapping for access info
PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.public_ipaddr')
PUBLIC_PORT=$(echo "$INSTANCE_INFO" | jq -r '.ports."8080/tcp"[0].HostPort')

echo ""
print_success "Deployment successful!"
echo ""
echo "🌐 Access your API:"
echo "   API URL: http://${PUBLIC_IP}:${PUBLIC_PORT}"
echo "   API Docs: http://${PUBLIC_IP}:${PUBLIC_PORT}/docs"
echo "   Health Check: http://${PUBLIC_IP}:${PUBLIC_PORT}/health"
echo ""
echo "🔧 SSH Access:"
echo "   ssh -p ${SSH_PORT} root@${SSH_HOST}"
echo ""
echo "📋 View logs:"
echo "   ssh -p ${SSH_PORT} root@${SSH_HOST} 'tail -f ~/logo_generator_backend/app.log'"
echo ""

