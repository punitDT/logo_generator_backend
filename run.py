"""
Application Entry Point
Run this file to start the AI Logo Generator server (GPU Mode)
"""

import sys
import uvicorn
from app.config import Config

if __name__ == "__main__":
    # Check for CUDA availability
    try:
        import torch
        if not torch.cuda.is_available():
            print("=" * 60)
            print("⚠️  WARNING: CUDA is not available!")
            print("This application requires GPU support to run.")
            print("Please ensure you are running on a GPU-enabled machine.")
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
    print("🚀 Starting AI Logo Generator Server (GPU Mode)")
    print("=" * 60)
    print(f"📍 Host: {Config.HOST}:{Config.PORT}")
    print(f"🤖 Model: {Config.get_model_identifier()}")
    print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
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

