"""
Application Entry Point
Run this file to start the AI Logo Generator server
"""

import os
import uvicorn
from app.config import Config

if __name__ == "__main__":
    # Determine if running in production
    is_production = os.getenv("RENDER") is not None or os.getenv("PRODUCTION") == "true"

    print("=" * 60)
    print("🚀 Starting AI Logo Generator Server")
    print("=" * 60)
    print(f"📍 Port: {Config.PORT}")
    print(f"🤖 Model: {Config.MODEL_NAME}")
    print(f"🔗 Provider: {Config.PROVIDER}")
    print(f"🌍 Environment: {'Production' if is_production else 'Development'}")
    if not is_production:
        print(f"📚 API Docs: http://localhost:{Config.PORT}/docs")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=Config.PORT,
        reload=not is_production,  # Only enable auto-reload in development
        log_level="info"
    )

