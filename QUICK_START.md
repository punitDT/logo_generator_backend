# ⚡ Quick Start Guide - AI Logo Generator GPU

**Get your GPU-powered logo generator running in 5 minutes!**

---

## 🎯 Prerequisites

- [ ] Vast.ai account with funds
- [ ] SSH key added to Vast.ai
- [ ] Basic terminal knowledge

---

## 🚀 Deployment Steps

### 1️⃣ Rent GPU on Vast.ai

1. Go to https://cloud.vast.ai/create/
2. Filter:
   - GPU: RTX 4090 (recommended) or RTX 3090
   - CUDA: 12.1+
   - Disk: 50GB+
3. Click **Rent** on a suitable instance
4. Wait for instance to start (~30 seconds)

### 2️⃣ Connect via SSH

```bash
# Copy SSH command from Vast.ai console
ssh -p <PORT> root@<IP_ADDRESS>
```

### 3️⃣ Clone & Setup

```bash
# Clone repository
git clone https://github.com/punitDT/logo_generator_backend.git
cd logo_generator_backend

# Create environment file
cp .env.example .env
```

### 4️⃣ Build Docker Image

```bash
docker build -t logo-generator-gpu .
```

⏱️ **Takes ~5-10 minutes** (downloads CUDA, Python packages)

### 5️⃣ Run Container

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

### 6️⃣ Monitor Startup

```bash
# Watch logs
docker logs -f logo-generator

# Wait for:
# ✅ Model loaded successfully!
# ✅ GPU warmup complete!
# ✅ Server ready to accept requests!
```

⏱️ **First startup takes ~5-10 minutes** (downloads Flux model)

### 7️⃣ Test API

```bash
# Health check
curl http://localhost:7860/health

# Generate test logo
curl -X POST http://localhost:7860/api/generate_logo \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Modern tech startup logo", "sizes": [512]}'
```

---

## 🌐 Access from Outside

Your API is accessible at:
```
http://<VAST_IP>:<VAST_EXTERNAL_PORT>
```

Find the external port in Vast.ai console (usually different from 7860).

**Example:**
- Internal: `localhost:7860`
- External: `123.45.67.89:12345`

---

## 📱 Update Flutter App

Change API endpoint in your Flutter app:

```dart
// Before
final apiUrl = 'http://localhost:8003';

// After
final apiUrl = 'http://<VAST_IP>:<VAST_PORT>';
```

---

## 🧪 Test with Python

```python
import requests
import base64

API_URL = "http://<VAST_IP>:<VAST_PORT>"

response = requests.post(
    f"{API_URL}/api/generate_logo",
    json={"prompt": "Minimalist AI logo", "sizes": [512]}
)

if response.status_code == 200:
    data = response.json()
    img_data = base64.b64decode(data['images']['512'])
    with open('logo.png', 'wb') as f:
        f.write(img_data)
    print("✅ Logo saved!")
```

---

## 🔍 Useful Commands

```bash
# View logs
docker logs -f logo-generator

# Check GPU usage
nvidia-smi

# Restart container
docker restart logo-generator

# Stop container
docker stop logo-generator

# Remove container
docker rm logo-generator

# Check container status
docker ps -a
```

---

## ⚙️ Quick Configuration

Edit `.env` for common adjustments:

```bash
# Faster but lower quality
DEFAULT_INFERENCE_STEPS=20

# More concurrent requests (if you have GPU memory)
MAX_CONCURRENT_JOBS=3

# Text logs for debugging
LOG_FORMAT=text
```

Then restart:
```bash
docker restart logo-generator
```

---

## 💰 Cost Tracking

- RTX 4090: ~$0.40-0.60/hour
- Check Vast.ai billing: https://cloud.vast.ai/billing/

**Don't forget to stop instance when not in use!**

---

## 🐛 Common Issues

### Issue: "CUDA out of memory"
**Fix:** Reduce concurrent jobs
```bash
# In .env
MAX_CONCURRENT_JOBS=1
```

### Issue: "Port not accessible"
**Fix:** Use external port from Vast.ai console, not 7860

### Issue: "First request very slow"
**Expected:** Model loading takes 2-5 minutes first time
**Fix:** Enable warmup in `.env`:
```bash
WARMUP_ENABLED=true
```

### Issue: "Container keeps restarting"
**Check logs:**
```bash
docker logs logo-generator
```

---

## 📊 Performance Tips

**For faster generation:**
- Use `DEFAULT_INFERENCE_STEPS=20` (vs 28)
- Enable `USE_FP16=true` (already default)
- Use smaller sizes first, then upscale

**For better quality:**
- Use `DEFAULT_INFERENCE_STEPS=50`
- Generate at max size (1024)

---

## 🎯 Success Checklist

- [ ] GPU instance rented
- [ ] SSH connection working
- [ ] Docker image built
- [ ] Container running
- [ ] Health check returns GPU stats
- [ ] Test generation successful
- [ ] External URL accessible
- [ ] Flutter app connected

---

## 📚 Need More Help?

- **Full Guide:** VASTAI_DEPLOYMENT.md
- **Troubleshooting:** VASTAI_DEPLOYMENT.md#troubleshooting
- **Configuration:** .env.example
- **Testing:** test_gpu_api.py

---

## 🎉 You're Done!

Your GPU-powered logo generator is now running!

**API Endpoints:**
- Health: `GET http://<VAST_IP>:<PORT>/health`
- Generate: `POST http://<VAST_IP>:<PORT>/api/generate_logo`
- Docs: `http://<VAST_IP>:<PORT>/docs`

**Happy generating! 🚀**

