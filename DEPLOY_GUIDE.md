# 🚀 Quick Deployment Guide for Vast.ai

This guide will help you deploy your Logo Generator backend to Vast.ai using the automated deployment scripts.

## 📋 Prerequisites

✅ Vast.ai CLI installed (`pip install vastai`)  
✅ Vast.ai account with API key configured  
✅ Instance details from GPU orchestrator  

## 🎯 Quick Start (3 Steps)

### Step 1: Configure Your Instance

Edit `vastai_config.json` and add your instance ID:

```json
{
  "instance_id": "YOUR_INSTANCE_ID_HERE",
  ...
}
```

**OR** set environment variable:
```bash
export VAST_INSTANCE_ID=your_instance_id
```

### Step 2: Configure Environment (Optional)

Copy the production environment template:
```bash
cp .env.vastai .env
```

Edit `.env` if you need to customize:
- `MAX_CONCURRENT_JOBS` - Based on your GPU VRAM
- `HF_TOKEN` - Your HuggingFace token (if needed)
- `WARMUP_ENABLED` - Set to `true` for production

### Step 3: Deploy!

Make scripts executable and deploy:
```bash
chmod +x deploy_vastai.sh vastai_*.sh
./deploy_vastai.sh
```

That's it! The script will:
1. ✅ Connect to your Vast.ai instance
2. ✅ Clone/update the repository
3. ✅ Copy your .env configuration
4. ✅ Build the Docker image
5. ✅ Start the container with GPU support
6. ✅ Display access URLs

## 📊 Post-Deployment

### Check Status
```bash
./vastai_status.sh
```

Shows:
- Instance information
- Container status
- API health check
- GPU utilization
- Access URLs

### View Logs
```bash
./vastai_logs.sh
```

Streams live logs from the container.

### Restart Container
```bash
./vastai_restart.sh
```

Restarts the container without rebuilding.

## 🌐 Access Your API

After deployment, you'll see:

```
🌐 Access your API:
   API URL: http://123.45.67.89:7860
   API Docs: http://123.45.67.89:7860/docs
   Health Check: http://123.45.67.89:7860/health
```

### Test the API

```bash
# Health check
curl http://YOUR_IP:7860/health

# Generate a logo
curl -X POST http://YOUR_IP:7860/api/generate_logo \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Modern tech startup logo",
    "sizes": [512, 1024]
  }'
```

## 🔧 Troubleshooting

### Issue: "Cannot access instance"
**Solution**: Check your instance ID and ensure it's running
```bash
vastai show instances
```

### Issue: "Container not starting"
**Solution**: Check logs for errors
```bash
./vastai_logs.sh
```

### Issue: "CUDA out of memory"
**Solution**: Reduce concurrent jobs in `.env`
```bash
MAX_CONCURRENT_JOBS=1
```
Then redeploy:
```bash
./deploy_vastai.sh
```

### Issue: "Model download fails"
**Solution**: Add HuggingFace token to `.env`
```bash
HF_TOKEN=your_token_here
```

## 🎮 GPU Configuration

Recommended settings based on GPU:

| GPU Model | VRAM | MAX_CONCURRENT_JOBS | WARMUP_ENABLED |
|-----------|------|---------------------|----------------|
| RTX 3090  | 24GB | 1-2                 | true           |
| RTX 4090  | 24GB | 2-3                 | true           |
| A6000     | 48GB | 3-4                 | true           |
| A100      | 40GB | 3-5                 | true           |

## 📝 Manual Deployment (Alternative)

If you prefer manual deployment, see [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md) for detailed step-by-step instructions.

## 🔄 Updating Your Deployment

To update to the latest code:

```bash
# The deploy script automatically pulls latest changes
./deploy_vastai.sh
```

Or manually:
```bash
# SSH into instance
vastai ssh-url YOUR_INSTANCE_ID

# Update code
cd logo_generator_backend
git pull

# Rebuild and restart
docker build -t logo-generator-gpu .
docker stop logo-generator
docker rm logo-generator
docker run -d --name logo-generator --gpus all -p 7860:7860 \
  -v $(pwd)/.env:/app/.env \
  -v /root/.cache/huggingface:/root/.cache/huggingface \
  --restart unless-stopped logo-generator-gpu
```

## 💡 Tips

1. **First deployment takes longer** - Model download can take 5-10 minutes
2. **Enable warmup in production** - Set `WARMUP_ENABLED=true` in `.env`
3. **Monitor GPU usage** - Use `./vastai_status.sh` regularly
4. **Keep HuggingFace cache** - The `-v /root/.cache/huggingface` mount saves model downloads
5. **Use auto-restart** - The `--restart unless-stopped` flag ensures container restarts after crashes

## 🆘 Need Help?

- Check [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md) for detailed documentation
- View logs: `./vastai_logs.sh`
- Check status: `./vastai_status.sh`
- Vast.ai docs: https://vast.ai/docs

---

**Happy Deploying! 🎉**

