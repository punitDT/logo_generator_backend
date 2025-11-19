# 🤖 Vast.ai Deployment Automation

Automated deployment scripts for deploying the Logo Generator backend to Vast.ai GPU instances.

## 📦 What's Included

### Core Scripts

1. **`vastai_setup.sh`** - Interactive setup wizard
   - Configures Vast.ai CLI
   - Selects instance
   - Creates configuration files

2. **`deploy_vastai.sh`** - Main deployment script
   - Clones/updates repository
   - Builds Docker image
   - Deploys container with GPU support
   - Shows access URLs

3. **`vastai_status.sh`** - Status checker
   - Instance information
   - Container status
   - API health check
   - GPU utilization

4. **`vastai_logs.sh`** - Log viewer
   - Streams live container logs
   - Useful for debugging

5. **`vastai_restart.sh`** - Quick restart
   - Restarts container without rebuilding

### Configuration Files

- **`vastai_config.json`** - Instance configuration
- **`.env.vastai`** - Production environment template

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Step 1: Run setup wizard
./vastai_setup.sh

# Step 2: Deploy
./deploy_vastai.sh
```

### Option 2: Manual Configuration

```bash
# Step 1: Edit config
nano vastai_config.json
# Add your instance_id

# Step 2: Copy environment
cp .env.vastai .env
# Edit .env if needed

# Step 3: Deploy
./deploy_vastai.sh
```

## 📋 Prerequisites

- ✅ Vast.ai account
- ✅ Vast.ai CLI installed: `pip install vastai`
- ✅ API key configured: `vastai set api-key YOUR_KEY`
- ✅ GPU instance rented on Vast.ai

## 🎯 Deployment Workflow

```
┌─────────────────┐
│  vastai_setup   │  Configure instance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ deploy_vastai   │  Deploy application
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ vastai_status   │  Check deployment
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  vastai_logs    │  Monitor logs
└─────────────────┘
```

## 🔧 Configuration

### Instance Configuration (`vastai_config.json`)

```json
{
  "instance_id": "YOUR_INSTANCE_ID",
  "image_name": "logo-generator-gpu",
  "container_name": "logo-generator",
  "app_port": 7860
}
```

### Environment Variables (`.env`)

Key settings for Vast.ai deployment:

```bash
# Server
PORT=7860
HOST=0.0.0.0
ENVIRONMENT=production

# Model
MODEL_NAME=black-forest-labs/FLUX.1-dev
USE_FP16=true

# GPU
MAX_CONCURRENT_JOBS=2  # Adjust based on GPU VRAM
WARMUP_ENABLED=true    # Warm up on startup

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# HuggingFace (optional)
HF_TOKEN=your_token_here
```

## 📊 Usage Examples

### Deploy Application
```bash
./deploy_vastai.sh
```

### Check Status
```bash
./vastai_status.sh
```

Output:
```
========================================
📊 Deployment Status
========================================
🖥️  Instance Information:
   Instance ID: 12345
   Public IP: 123.45.67.89
   GPU: NVIDIA RTX 4090
   
🐳 Container Status:
   Status: ✅ Running
   
🏥 API Health Check:
   ✅ API is healthy
   
🎮 GPU Status:
   GPU: NVIDIA RTX 4090
   Memory: 8192 MB / 24576 MB (33.3%)
   Utilization: 45%
```

### View Logs
```bash
./vastai_logs.sh
```

### Restart Container
```bash
./vastai_restart.sh
```

## 🔍 Troubleshooting

### Script Fails with "Instance not found"

**Solution**: Run setup again
```bash
./vastai_setup.sh
```

### Container Won't Start

**Solution**: Check logs
```bash
./vastai_logs.sh
```

Common issues:
- CUDA out of memory → Reduce `MAX_CONCURRENT_JOBS`
- Model download fails → Add `HF_TOKEN` to `.env`
- Port conflict → Check if port 7860 is available

### API Not Responding

**Solution**: Check status and wait for model loading
```bash
./vastai_status.sh
```

First startup takes 5-10 minutes for model download.

## 🎮 GPU-Specific Settings

Recommended `MAX_CONCURRENT_JOBS` by GPU:

| GPU       | VRAM  | Jobs | Notes                    |
|-----------|-------|------|--------------------------|
| RTX 3090  | 24GB  | 1-2  | Good for testing         |
| RTX 4090  | 24GB  | 2-3  | Best price/performance   |
| A6000     | 48GB  | 3-4  | High reliability         |
| A100      | 40GB  | 3-5  | Enterprise grade         |

## 📝 Environment Variables

Set instance ID via environment:
```bash
export VAST_INSTANCE_ID=12345
./deploy_vastai.sh
```

Or use config file (recommended).

## 🔄 Updating Deployment

To update to latest code:
```bash
./deploy_vastai.sh
```

The script automatically:
1. Pulls latest code from GitHub
2. Rebuilds Docker image
3. Restarts container

## 🆘 Getting Help

1. **Check logs**: `./vastai_logs.sh`
2. **Check status**: `./vastai_status.sh`
3. **Review docs**: See [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)
4. **Manual deployment**: See [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md)

## 📚 Additional Resources

- [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) - Quick deployment guide
- [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md) - Detailed manual deployment
- [Vast.ai Docs](https://vast.ai/docs) - Official documentation

---

**Made with ❤️ for easy GPU deployment**

