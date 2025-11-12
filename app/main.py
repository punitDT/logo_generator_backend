"""
AI Logo Generator - Main Application
FastAPI application for generating professional logos using AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.generate_logo_routes import router as logo_router
from app.config import Config

# Create FastAPI application
app = FastAPI(
    title="AI Logo Generator",
    description="Generate professional logos from text using Hugging Face Inference API (FLUX.1-dev). "
                "Automatically enhances prompts for clean, minimalist, brand-ready designs.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
def root():
    """Root endpoint - API health check"""
    return {
        "message": "🚀 AI Logo Generator API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": Config.MODEL_NAME,
        "provider": Config.PROVIDER
    }

