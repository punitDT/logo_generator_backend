# 🎨 AI Logo Generator - GPU Edition

**Production-ready FastAPI backend for AI logo generation using local GPU inference with Flux model.**

This is a complete refactor of the original HuggingFace API-based backend to run **entirely on GPU** using local model inference, optimized for deployment on **Vast.ai** or any CUDA-enabled GPU machine.

---

## ✨ Key Features

- **🚀 Local GPU Inference**: Runs Flux model directly on GPU (no external API calls)
- **⚡ High Performance**: FP16 precision, attention slicing, concurrent request handling
- **🔄 Production Ready**: Async FastAPI, JSON logging, health monitoring, exception handling
- **🎯 Optimized for Vast.ai**: Docker container with CUDA support, automatic GPU warmup
- **📊 Monitoring**: GPU stats, request tracking, detailed logging
- **🔧 Configurable**: Environment-based configuration for all parameters
- **💰 Cost Effective**: Run on affordable GPU instances (~$0.20-0.60/hour)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routes     │  │  Middleware  │  │   Logging    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Model Manager (Singleton)               │
│  • Load Flux model once at startup                      │
│  • Manage GPU memory and concurrency                    │
│  • Async inference with semaphore control               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    GPU (CUDA)                            │
│  • Flux.1-dev model in FP16                             │
│  • Attention slicing for memory optimization            │
│  • Concurrent inference (configurable)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 What's New in GPU Edition

### Removed
- ❌ HuggingFace Inference API dependency
- ❌ External API calls
- ❌ API token requirements (for inference)

### Added
- ✅ Local GPU model loading with `diffusers`
- ✅ Model manager with singleton pattern
- ✅ Async inference with concurrency control
- ✅ GPU warmup on startup
- ✅ JSON structured logging
- ✅ Health endpoint with GPU stats
- ✅ Exception handling middleware
- ✅ CUDA-compatible Dockerfile
- ✅ Vast.ai deployment guide

---

## 🚀 Quick Start

### Prerequisites
- **GPU**: NVIDIA GPU with 24GB+ VRAM (RTX 3090, 4090, A6000, etc.)
- **CUDA**: Version 12.1+
- **Docker**: With NVIDIA Container Toolkit
- **OR** Python 3.10+ with CUDA support

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/punitDT/logo_generator_backend.git
cd logo_generator_backend

# Create environment file
cp .env.example .env

# Build image
docker build -t logo-generator-gpu .

# Run container
docker run -d \
  --name logo-generator \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/.env:/app/.env \
  -v /root/.cache/huggingface:/root/.cache/huggingface \
  logo-generator-gpu

# Check logs
docker logs -f logo-generator
```

### Option 2: Direct Python

```bash
# Clone repository
git clone https://github.com/punitDT/logo_generator_backend.git
cd logo_generator_backend

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Run server
python run.py
```

---

## 📚 API Documentation

### Endpoints

#### `GET /health`
Health check with GPU status

**Response:**
```json
{
  "status": "healthy",
  "model": "black-forest-labs/FLUX.1-dev",
  "model_loaded": true,
  "gpu": {
    "gpu_available": true,
    "device_name": "NVIDIA RTX 4090",
    "memory_allocated_gb": 15.2,
    "memory_total_gb": 24.0
  }
}
```

#### `POST /api/generate_logo`
Generate professional logos

**Request:**
```json
{
  "prompt": "Modern tech startup logo",
  "sizes": [256, 512, 1024]
}
```

**Response:**
```json
{
  "message": "Logo generated successfully!",
  "prompt": "Modern tech startup logo",
  "images": {
    "256": "base64_encoded_image...",
    "512": "base64_encoded_image...",
    "1024": "base64_encoded_image..."
  },
  "sizes": [256, 512, 1024],
  "model": "black-forest-labs/FLUX.1-dev"
}
```

---

## ⚙️ Configuration

Key environment variables (see `.env.example` for all options):

```bash
# Model
MODEL_NAME=black-forest-labs/FLUX.1-dev
USE_FP16=true

# GPU
MAX_CONCURRENT_JOBS=2
REQUEST_TIMEOUT=300

# Inference
DEFAULT_INFERENCE_STEPS=28
DEFAULT_GUIDANCE_SCALE=3.5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## 🌐 Vast.ai Deployment

See **[VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md)** for complete deployment guide.

**Quick Deploy:**
1. Rent GPU on Vast.ai (RTX 4090 recommended)
2. SSH into instance
3. Clone repo and run Docker container
4. Access API at `http://<VAST_IP>:<VAST_PORT>`

**Estimated Costs:**
- RTX 3090: $0.20-0.40/hour
- RTX 4090: $0.40-0.60/hour
- A6000: $0.60-1.00/hour

---

## 📊 Performance

**RTX 4090 Benchmarks:**
- 512x512 @ 28 steps: ~12 seconds
- 1024x1024 @ 28 steps: ~18 seconds
- Concurrent (2 jobs): ~25 seconds total

---

## 🗂️ Project Structure

```
logo_generator_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with lifespan events
│   ├── config.py               # GPU configuration
│   ├── model_manager.py        # Singleton model manager
│   ├── logging_config.py       # JSON/text logging
│   ├── routes/
│   │   └── generate_logo_routes.py
│   └── services/
│       └── generate_logo_service.py  # GPU inference logic
├── run.py                      # Entry point with GPU checks
├── requirements.txt            # GPU dependencies
├── Dockerfile                  # CUDA-compatible image
├── .env.example               # Configuration template
├── VASTAI_DEPLOYMENT.md       # Deployment guide
└── README_GPU.md              # This file
```

---

## 🔧 Development

```bash
# Install in development mode
pip install -r requirements.txt

# Run with auto-reload
ENVIRONMENT=development python run.py

# View logs in text format
LOG_FORMAT=text python run.py

# Access API docs
http://localhost:7860/docs
```

---

## 🐛 Troubleshooting

See [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md#-monitoring--troubleshooting) for detailed troubleshooting.

**Common Issues:**
- **CUDA Out of Memory**: Reduce `MAX_CONCURRENT_JOBS` or `DEFAULT_INFERENCE_STEPS`
- **Slow First Request**: Model loading takes 2-5 minutes (enable warmup)
- **Port Not Accessible**: Check Vast.ai port forwarding

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Flux Model**: [Black Forest Labs](https://huggingface.co/black-forest-labs/FLUX.1-dev)
- **Diffusers**: [HuggingFace Diffusers](https://github.com/huggingface/diffusers)
- **FastAPI**: [Tiangolo](https://fastapi.tiangolo.com)

---

**🚀 Ready to deploy? Check out [VASTAI_DEPLOYMENT.md](VASTAI_DEPLOYMENT.md)!**

