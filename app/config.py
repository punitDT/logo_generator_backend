"""
Configuration module for AI Logo Generator
Handles environment variables and GPU model configuration
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class for GPU-based inference"""

    # Server Configuration
    PORT: int = int(os.getenv("PORT", 7860))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")

    # Model Configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "black-forest-labs/FLUX.1-dev")
    MODEL_PATH: Optional[str] = os.getenv("MODEL_PATH", None)  # For local model files
    USE_FP16: bool = os.getenv("USE_FP16", "true").lower() == "true"

    # GPU Configuration
    # Auto-detect device: cuda (NVIDIA) > mps (Apple Silicon) > cpu
    TORCH_DEVICE: str = os.getenv("TORCH_DEVICE", "auto")
    ENABLE_ATTENTION_SLICING: bool = os.getenv("ENABLE_ATTENTION_SLICING", "true").lower() == "true"
    ENABLE_VAE_SLICING: bool = os.getenv("ENABLE_VAE_SLICING", "true").lower() == "true"

    # Inference Configuration
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", 2))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 300))  # seconds
    DEFAULT_INFERENCE_STEPS: int = int(os.getenv("DEFAULT_INFERENCE_STEPS", 28))
    DEFAULT_GUIDANCE_SCALE: float = float(os.getenv("DEFAULT_GUIDANCE_SCALE", 3.5))

    # Logo Generation Settings
    DEFAULT_SIZES: list[int] = [256, 512, 1024]
    MAX_SIZE: int = 2048
    MIN_SIZE: int = 64

    # Warmup Configuration
    WARMUP_ENABLED: bool = os.getenv("WARMUP_ENABLED", "true").lower() == "true"
    WARMUP_PROMPT: str = os.getenv("WARMUP_PROMPT", "test logo")
    WARMUP_SIZE: int = int(os.getenv("WARMUP_SIZE", 256))
    WARMUP_STEPS: int = int(os.getenv("WARMUP_STEPS", 4))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        # Check if model name or path is provided
        if not cls.MODEL_NAME and not cls.MODEL_PATH:
            raise ValueError("❌ Either MODEL_NAME or MODEL_PATH must be set.")

        # Validate concurrent jobs
        if cls.MAX_CONCURRENT_JOBS < 1:
            raise ValueError("❌ MAX_CONCURRENT_JOBS must be at least 1.")

        print("✅ Configuration validated successfully.")

    @classmethod
    def get_model_identifier(cls) -> str:
        """Get the model identifier (path or name)"""
        return cls.MODEL_PATH if cls.MODEL_PATH else cls.MODEL_NAME

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.ENVIRONMENT.lower() == "production"


# Initialize and validate config
config = Config()
config.validate()

