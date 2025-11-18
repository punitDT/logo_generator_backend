"""
AI Logo Generator - Main Application
FastAPI application for generating professional logos using local GPU inference
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uuid
import logging

from app.routes.generate_logo_routes import router as logo_router
from app.config import Config
from app.model_manager import ModelManager
from app.logging_config import setup_logging, RequestLogger

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles model loading and GPU warmup on startup.
    """
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 Starting AI Logo Generator Server (GPU Mode)")
    logger.info("=" * 60)
    logger.info(f"📍 Port: {Config.PORT}")
    logger.info(f"🤖 Model: {Config.get_model_identifier()}")
    logger.info(f"🔧 Environment: {Config.ENVIRONMENT}")
    logger.info(f"⚡ Max Concurrent Jobs: {Config.MAX_CONCURRENT_JOBS}")
    logger.info(f"🎯 FP16 Enabled: {Config.USE_FP16}")
    logger.info("=" * 60)

    try:
        # Initialize model manager
        model_manager = await ModelManager.get_instance(
            max_concurrent_jobs=Config.MAX_CONCURRENT_JOBS
        )

        # Load model
        await model_manager.load_model(
            model_name=Config.get_model_identifier(),
            use_fp16=Config.USE_FP16
        )

        # Perform warmup if enabled
        if Config.WARMUP_ENABLED:
            await model_manager.warmup(
                warmup_prompt=Config.WARMUP_PROMPT,
                size=Config.WARMUP_SIZE,
                steps=Config.WARMUP_STEPS
            )

        # Log GPU stats
        gpu_stats = model_manager.get_gpu_stats()
        logger.info(f"🎮 GPU Stats: {gpu_stats}")
        logger.info("✅ Server ready to accept requests!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to initialize server: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down server...")
    try:
        model_manager = await ModelManager.get_instance()
        model_manager.cleanup()
        logger.info("✅ Cleanup complete")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="AI Logo Generator (GPU)",
    description="Generate professional logos from text using local GPU Flux model inference. "
                "Automatically enhances prompts for clean, minimalist, brand-ready designs.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Exception handling middleware
@app.middleware("http")
async def exception_handling_middleware(request: Request, call_next):
    """Global exception handling and request logging"""
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Log request
    RequestLogger.log_request(
        logger,
        request_id=request_id,
        endpoint=request.url.path,
        method=request.method
    )

    try:
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        RequestLogger.log_response(
            logger,
            request_id=request_id,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Request failed: {str(e)}",
            extra={
                "request_id": request_id,
                "endpoint": request.url.path,
                "duration_ms": duration_ms
            },
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Internal server error",
                "request_id": request_id
            }
        )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    logo_router,
    prefix="/api",
    tags=["Logo Generator"]
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "🚀 AI Logo Generator API is running (GPU Mode)!",
        "version": "2.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with GPU status"""
    try:
        model_manager = await ModelManager.get_instance()
        gpu_stats = model_manager.get_gpu_stats()

        return {
            "status": "healthy",
            "model": Config.get_model_identifier(),
            "model_loaded": model_manager.model_loaded,
            "gpu": gpu_stats,
            "environment": Config.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

