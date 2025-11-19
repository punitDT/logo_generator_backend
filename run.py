"""
Application Entry Point
Run this file to start the AI Logo Generator server (GPU Mode)
"""

import sys
import uvicorn
from app.config import Config

if __name__ == "__main__":
    # Check for GPU availability (CUDA or MPS)
    try:
        import torch

        # Detect available device
        if torch.cuda.is_available():
            device = "cuda"
            device_name = torch.cuda.get_device_name(0)
            device_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        elif torch.backends.mps.is_available():
            device = "mps"
            device_name = "Apple Silicon GPU (MPS)"
            device_memory = "Shared with system RAM"
        else:
            print("=" * 60)
            print("⚠️  WARNING: No GPU acceleration available!")
            print("This application requires GPU support (CUDA or MPS) to run efficiently.")
            print("For Apple Silicon Macs, ensure PyTorch with MPS support is installed.")
            print("For NVIDIA GPUs, ensure CUDA is properly configured.")
            print("=" * 60)
            sys.exit(1)

    except ImportError:
        print("=" * 60)
        print("❌ ERROR: PyTorch is not installed!")
        print("Please install requirements: pip install -r requirements.txt")
        print("=" * 60)
        sys.exit(1)

    # Determine if running in production
    is_production = Config.is_production()

    print("=" * 60)
    print(f"🚀 Starting AI Logo Generator Server ({device.upper()} Mode)")
    print("=" * 60)
    print(f"📍 Host: {Config.HOST}:{Config.PORT}")
    print(f"🤖 Model: {Config.get_model_identifier()}")
    print(f"🎮 Device: {device_name}")
    if isinstance(device_memory, float):
        print(f"💾 GPU Memory: {device_memory:.2f} GB")
    else:
        print(f"💾 Memory: {device_memory}")
    print(f"🌍 Environment: {Config.ENVIRONMENT}")
    print(f"⚡ Max Concurrent Jobs: {Config.MAX_CONCURRENT_JOBS}")
    print(f"🎯 FP16: {Config.USE_FP16}")
    if not is_production:
        print(f"📚 API Docs: http://{Config.HOST}:{Config.PORT}/docs")
    print("=" * 60)

    # Run server
    uvicorn.run(
        "app.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=not is_production,  # Only enable auto-reload in development
        log_level=Config.LOG_LEVEL.lower(),
        access_log=not is_production
    )

