# 🚀 Vast.ai GPU Deployment Guide

Complete guide for deploying the AI Logo Generator backend on Vast.ai GPU instances.

---

## 📋 Prerequisites

1. **Vast.ai Account**: Sign up at [vast.ai](https://vast.ai)
2. **SSH Key**: Generate and add your SSH public key to Vast.ai
3. **Docker Knowledge**: Basic understanding of Docker
4. **Git Repository**: Your code pushed to GitHub

---

## 🎯 Quick Start (Recommended)

### Option 1: Direct Docker Deployment

1. **Rent a GPU Instance on Vast.ai**
   - Go to [Vast.ai Console](https://cloud.vast.ai/create/)
   - Filter by:
     - GPU: RTX 3090, RTX 4090, or A6000 (24GB+ VRAM recommended)
     - CUDA Version: 12.1+
     - Disk Space: 50GB+
   - Select "pytorch/pytorch" or "nvidia/cuda" template
   - Click "Rent"

2. **SSH into Your Instance**
   ```bash
   ssh -p <PORT> root@<IP_ADDRESS>
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/punitDT/logo_generator_backend.git
   cd logo_generator_backend
   ```

4. **Create Environment File**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults should work)
   nano .env
   ```

5. **Build Docker Image**
   ```bash
   docker build -t logo-generator-gpu .
   ```

6. **Run Container**
   ```bash
   docker run -d \
     --name logo-generator \
     --gpus all \
     -p 7860:7860 \
     -v $(pwd)/.env:/app/.env \
     -v /root/.cache/huggingface:/root/.cache/huggingface \
     --restart unless-stopped \
     logo-generator-gpu
   ```

7. **Check Logs**
   ```bash
   docker logs -f logo-generator
   ```

8. **Access API**
   - API: `http://<VAST_IP>:<VAST_PORT>`
   - Docs: `http://<VAST_IP>:<VAST_PORT>/docs`

---

## 🔧 Option 2: Manual Installation (Without Docker)

### Step 1: Rent GPU Instance
Same as Option 1, step 1.

### Step 2: SSH and Setup Environment
```bash
ssh -p <PORT> root@<IP_ADDRESS>

# Update system
apt-get update && apt-get upgrade -y

# Install Python 3.10+
apt-get install -y python3.10 python3-pip git

# Clone repository
git clone https://github.com/punitDT/logo_generator_backend.git
cd logo_generator_backend
```

### Step 3: Install Dependencies
```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit if needed
nano .env
```

### Step 5: Run Server
```bash
# Run directly
python run.py

# OR run with nohup for background
nohup python run.py > server.log 2>&1 &
```

---

## ⚙️ Configuration

### Environment Variables (.env)





```bash
# Server
PORT=7860                    # API port
ENVIRONMENT=production       # production or development

# Model
MODEL_NAME=black-forest-labs/FLUX.1-dev  # HuggingFace model
USE_FP16=true               # Use FP16 for faster inference

# GPU
MAX_CONCURRENT_JOBS=2       # Adjust based on GPU memory
REQUEST_TIMEOUT=300         # Request timeout in seconds

# Inference
DEFAULT_INFERENCE_STEPS=28  # Quality vs speed tradeoff
DEFAULT_GUIDANCE_SCALE=3.5  # Prompt adherence

# Logging
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json            # json or text
```

### GPU Memory Recommendations

| GPU Model | VRAM | MAX_CONCURRENT_JOBS | Recommended Steps |
|-----------|------|---------------------|-------------------|
| RTX 3090  | 24GB | 1-2                 | 20-28             |
| RTX 4090  | 24GB | 2-3                 | 28-50             |
| A6000     | 48GB | 3-4                 | 28-50             |
| A100      | 40GB | 3-5                 | 28-50             |

---

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl http://<VAST_IP>:<VAST_PORT>/health
```

Expected response:
```json
{
  "status": "healthy",
  "model": "black-forest-labs/FLUX.1-dev",
  "model_loaded": true,
  "gpu": {
    "gpu_available": true,
    "device_name": "NVIDIA RTX 4090",
    "memory_allocated_gb": 15.2,
    "memory_reserved_gb": 16.0,
    "memory_total_gb": 24.0
  },
  "environment": "production"
}
```

### 2. Generate Logo Test
```bash
curl -X POST http://<VAST_IP>:<VAST_PORT>/api/generate_logo \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Modern tech startup logo",
    "sizes": [512]
  }'
```

### 3. Python Test Script
```python
import requests
import base64
from pathlib import Path

API_URL = "http://<VAST_IP>:<VAST_PORT>"

# Test generation
response = requests.post(
    f"{API_URL}/api/generate_logo",
    json={
        "prompt": "Minimalist AI company logo",
        "sizes": [256, 512, 1024]
    }
)

if response.status_code == 200:
    data = response.json()

    # Save images
    for size, base64_img in data['images'].items():
        img_data = base64.b64decode(base64_img)
        Path(f"logo_{size}px.png").write_bytes(img_data)
        print(f"✅ Saved logo_{size}px.png")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
```

---

## 🔍 Monitoring & Troubleshooting

### Check GPU Usage
```bash
# Install nvidia-smi if not available
nvidia-smi

# Watch GPU usage in real-time
watch -n 1 nvidia-smi
```

### View Logs
```bash
# Docker logs
docker logs -f logo-generator

# Direct run logs
tail -f server.log

# Check for errors
docker logs logo-generator 2>&1 | grep ERROR
```

### Common Issues

#### 1. CUDA Out of Memory
**Solution**: Reduce `MAX_CONCURRENT_JOBS` or `DEFAULT_INFERENCE_STEPS`
```bash
# In .env
MAX_CONCURRENT_JOBS=1
DEFAULT_INFERENCE_STEPS=20
```

#### 2. Model Download Fails
**Solution**: Check internet connection and HuggingFace access
```bash
# Test HuggingFace connection
curl -I https://huggingface.co

# Pre-download model
python -c "from diffusers import FluxPipeline; FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-dev')"
```

#### 3. Port Not Accessible
**Solution**: Check Vast.ai port forwarding
- Vast.ai automatically maps internal port 7860 to an external port
- Use the external port shown in Vast.ai console

#### 4. Slow First Request
**Expected**: First request triggers model loading (~2-5 minutes)
- Subsequent requests are fast
- Enable `WARMUP_ENABLED=true` to warm up on startup


---

## 🚀 Production Optimizations

### 1. Use Pre-downloaded Model
```bash
# Download model once
python -c "from diffusers import FluxPipeline; FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-dev', cache_dir='/models')"

# Update .env
MODEL_PATH=/models/models--black-forest-labs--FLUX.1-dev
```

### 2. Enable Model Caching
```bash
# Mount cache volume in Docker
docker run -d \
  --gpus all \
  -p 7860:7860 \
  -v /root/.cache/huggingface:/root/.cache/huggingface \
  logo-generator-gpu
```

### 3. Use Nginx Reverse Proxy (Optional)
```bash
# Install nginx
apt-get install -y nginx

# Configure nginx
cat > /etc/nginx/sites-available/logo-api << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
EOF

ln -s /etc/nginx/sites-available/logo-api /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx
```

---

## 💰 Cost Optimization

### Tips to Reduce Costs

1. **Choose Right GPU**
   - RTX 3090: ~$0.20-0.40/hour (good for testing)
   - RTX 4090: ~$0.40-0.60/hour (best performance/cost)
   - A6000: ~$0.60-1.00/hour (high reliability)

2. **Use Spot Instances**
   - Enable "Interruptible" for 50-70% discount
   - Good for development/testing

3. **Auto-shutdown**
   ```bash
   # Shutdown after 1 hour of inactivity
   echo "shutdown -h +60" | at now
   ```

4. **Monitor Usage**
   - Check Vast.ai billing regularly
   - Stop instances when not in use

---

## 📊 Performance Benchmarks

### Expected Generation Times (RTX 4090)

| Size    | Steps | Time    | Concurrent Jobs |
|---------|-------|---------|-----------------|
| 512x512 | 20    | ~8s     | 1               |
| 512x512 | 28    | ~12s    | 1               |
| 1024x1024 | 28  | ~18s    | 1               |
| 1024x1024 | 28  | ~25s    | 2 (parallel)    |

---

## 🔐 Security Best Practices

1. **Use Environment Variables**
   - Never commit `.env` to git
   - Use secrets for sensitive data

2. **Restrict API Access**
   - Add API key authentication if needed
   - Use Vast.ai firewall rules

3. **Update Regularly**
   ```bash
   git pull
   docker build -t logo-generator-gpu .
   docker stop logo-generator
   docker rm logo-generator
   # Run new container
   ```

---

## 📞 Support & Resources

- **Vast.ai Docs**: https://vast.ai/docs
- **Flux Model**: https://huggingface.co/black-forest-labs/FLUX.1-dev
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Issues**: https://github.com/punitDT/logo_generator_backend/issues

---

## ✅ Deployment Checklist

- [ ] Vast.ai account created and funded
- [ ] SSH key added to Vast.ai
- [ ] GPU instance rented (24GB+ VRAM)
- [ ] Repository cloned
- [ ] `.env` file configured
- [ ] Docker image built
- [ ] Container running
- [ ] Health check passing
- [ ] Test generation successful
- [ ] Monitoring setup
- [ ] Costs tracked

---

**🎉 You're all set! Your GPU-powered logo generator is now running on Vast.ai!**

