"""
Configuration module for AI Logo Generator
Handles environment variables and API client initialization
"""

import os
from typing import Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""
    
    # API Configuration
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Model Configuration
    MODEL_NAME: str = "black-forest-labs/FLUX.1-dev"
    PROVIDER: str = "nebius"
    
    # Logo Generation Settings
    DEFAULT_SIZES: list[int] = [256, 512, 1024]
    MAX_SIZE: int = 2048
    MIN_SIZE: int = 64
    
    # Validation
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.HF_TOKEN:
            raise ValueError("❌ HF_TOKEN is missing from environment variables.")
        print("✅ Configuration validated successfully.")
    
    @classmethod
    def get_client(cls) -> InferenceClient:
        """Get initialized Hugging Face Inference Client"""
        cls.validate()
        client = InferenceClient(
            provider=cls.PROVIDER,
            api_key=cls.HF_TOKEN,
        )
        print("✅ Hugging Face Inference Client initialized successfully.")
        return client


# Initialize client singleton
config = Config()
client = config.get_client()

